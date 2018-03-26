# -*- coding: utf-8 -*-

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, exceptions, status, mixins, filters
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework_filters import backends

from .. import models, serializers
from ..filters import (
    ComputerFilter, StoreFilter, PropertyFilter,
    ProjectFilter, AttributeSetFilter, AttributeFilter, PackageFilter,
    DeploymentFilter, ErrorFilter, FaultDefinitionFilter,
    FaultFilter, NotificationFilter, MigrationFilter,
    NodeFilter, SynchronizationFilter, StatusLogFilter,
    DeviceFilter, DriverFilter, ScheduleDelayFilter,
)
from ..tasks import create_repository_metadata


class AttributeSetViewSet(viewsets.ModelViewSet):
    queryset = models.AttributeSet.objects.all()
    serializer_class = serializers.AttributeSetSerializer
    filter_class = AttributeSetFilter
    ordering_fields = '__all__'
    ordering = ('name',)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.AttributeSetWriteSerializer

        return serializers.AttributeSetSerializer


class AttributeViewSet(viewsets.ModelViewSet):
    queryset = models.Attribute.objects.all()
    serializer_class = serializers.AttributeSerializer
    filter_class = AttributeFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)

    def get_queryset(self):
        user = self.request.user.userprofile
        qs = self.queryset
        if not user.is_view_all():
            qs = qs.filter(id__in=user.get_attributes()).distinct()

        return qs

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return serializers.AttributeWriteSerializer

        return serializers.AttributeSerializer

    @detail_route(methods=['get', 'put', 'patch'], url_path='logical-devices')
    def logical_devices(self, request, pk=None):
        """
        GET
            returns: [
                {
                    "id": 112,
                    "device": {
                        "id": 6,
                        "name": "19940"
                    },
                    "feature": {
                        "id": 2,
                        "name": "Color"
                    },
                    "name": ""
                },
                {
                    "id": 7,
                    "device": {
                        "id": 6,
                        "name": "19940"
                    },
                    "feature": {
                        "id": 1,
                        "name": "BN"
                    },
                    "name": ""
                }
            ]

        PUT, PATCH
            input: [id1, id2, idN]

            returns: status code 201
        """

        attribute = get_object_or_404(models.Attribute, pk=pk)
        logical_devices = attribute.devicelogical_set.all()

        if request.method == 'GET':
            serializer = serializers.LogicalSerializer(
                logical_devices,
                many=True
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'PATCH':  # append cid attribute to logical devices
            for device_id in request.data:
                device = get_object_or_404(models.DeviceLogical, pk=device_id)
                if device not in logical_devices:
                    device.attributes.add(pk)

            return Response(status=status.HTTP_201_CREATED)

        if request.method == 'PUT':  # replace cid attribute in logical devices
            for device in logical_devices:
                if device in logical_devices:
                    device.attributes.remove(pk)

            for device_id in request.data:
                device = get_object_or_404(models.DeviceLogical, pk=device_id)
                device.attributes.add(pk)

            return Response(status=status.HTTP_201_CREATED)


class ComputerViewSet(viewsets.ModelViewSet):
    queryset = models.Computer.objects.all()
    serializer_class = serializers.ComputerSerializer
    filter_class = ComputerFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return serializers.ComputerWriteSerializer

        return serializers.ComputerSerializer

    def partial_update(self, request, *args, **kwargs):
        data = dict(request.data.iterlists())
        devices = data.get('assigned_logical_devices_to_cid[]', data.get('assigned_logical_devices_to_cid', None))
        if devices:
            try:
                assigned_logical_devices_to_cid = map(int, devices)
            except ValueError:
                assigned_logical_devices_to_cid = []
            computer = get_object_or_404(models.Computer, pk=kwargs['pk'])
            computer.update_logical_devices(assigned_logical_devices_to_cid)

        return super(ComputerViewSet, self).partial_update(
            request,
            *args,
            **kwargs
        )

    def get_queryset(self):
        user = self.request.user.userprofile
        qs = self.queryset
        if not user.is_view_all():
            qs = qs.filter(id__in=user.get_computers())

        return qs

    @detail_route(methods=['get'], url_path='software/inventory')
    def software_inventory(self, request, pk=None):
        """
        Returns installed packages in a computer
        """
        computer = get_object_or_404(models.Computer, pk=pk)
        data = []
        if computer.software_inventory:
            data = computer.software_inventory.replace('+', '').split('\n')

        return Response(
            data,
            status=status.HTTP_200_OK
        )

    @detail_route(methods=['get'], url_path='software/history')
    def software_history(self, request, pk=None):
        """
        Returns software history of a computer
        """
        computer = get_object_or_404(models.Computer, pk=pk)

        return Response(
            computer.software_history,
            status=status.HTTP_200_OK
        )

    @detail_route(methods=['post'])
    def status(self, request, pk=None):
        """
        Input: {
            'status': 'available' | 'reserved' | 'unsubscribed' | 'unknown'
                | 'intended'
        }
        Changes computer status
        """
        computer = get_object_or_404(models.Computer, pk=pk)

        ret = computer.change_status(request.data.get('status'))
        if not ret:
            raise exceptions.ParseError(
                _('Status must have one of the values: %s') % (
                    dict(models.Computer.STATUS_CHOICES).keys()
                )
            )

        serializer = serializers.ComputerSerializer(computer, context={'request': request})
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @detail_route(methods=['post'])
    def replacement(self, request, pk=None):
        """
        Input: {
            'target': id
        }
        Exchanges tags and status
        """
        source = get_object_or_404(models.Computer, pk=pk)
        target = get_object_or_404(
            models.Computer, id=request.data.get('target')
        )

        models.Computer.replacement(source, target)

        return Response(status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def sync(self, request, pk=None):
        """
        :returns
            {
                "date": "Y-m-d H:M:s",
                "user": {
                    "id": x,
                    "name": "xxx",
                    "fullname": "xxxxx"
                },
                "attributes": [
                    {
                        "id": x,
                        "value": "xxx",
                        "description": "xxxxx",
                        "total_computers"; xx,
                        "property_att": {
                            "id": x,
                            "prefix": "xxx"
                        }
                    },
                    ...
                ]
            }
        """
        computer = get_object_or_404(models.Computer, pk=pk)
        serializer = serializers.ComputerSyncSerializer(computer, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class ErrorViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = models.Error.objects.all()
    serializer_class = serializers.ErrorSerializer
    filter_class = ErrorFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('-created_at',)

    def get_queryset(self):
        user = self.request.user.userprofile
        qs = self.queryset
        if not user.is_view_all():
            qs = qs.filter(
                project_id__in=user.get_projects(),
                computer_id__in=user.get_computers()
            )

        return qs

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return serializers.ErrorWriteSerializer

        return serializers.ErrorSerializer


class FaultDefinitionViewSet(viewsets.ModelViewSet):
    queryset = models.FaultDefinition.objects.all()
    serializer_class = serializers.FaultDefinitionSerializer
    filter_class = FaultDefinitionFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('name',)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.FaultDefinitionWriteSerializer

        return serializers.FaultDefinitionSerializer


class FaultViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = models.Fault.objects.all()
    serializer_class = serializers.FaultSerializer
    filter_class = FaultFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('-created_at',)

    def get_queryset(self):
        user = self.request.user.userprofile
        qs = self.queryset
        if not user.is_view_all():
            qs = qs.filter(
                project_id__in=user.get_projects(),
                computer_id__in=user.get_computers()
            )

        return qs

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return serializers.FaultWriteSerializer

        return serializers.FaultSerializer


class HardwareComputerViewSet(viewsets.ViewSet):
    queryset = models.HwNode.objects.all()  # FIXME

    @detail_route(methods=['get'])
    def hardware(self, request, pk=None):
        computer = get_object_or_404(models.Computer, pk=pk)
        nodes = models.HwNode.objects.filter(computer=computer).order_by('id')

        serializer = serializers.NodeSerializer(nodes, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class HardwareViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.HwNode.objects.all()
    serializer_class = serializers.NodeSerializer
    filter_class = NodeFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('id',)

    def get_queryset(self):
        user = self.request.user.userprofile
        qs = self.queryset
        if not user.is_view_all():
            qs = qs.filter(computer_id__in=user.get_computers())

        return qs


class MigrationViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = models.Migration.objects.all()
    serializer_class = serializers.MigrationSerializer
    filter_class = MigrationFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('-created_at',)

    def get_queryset(self):
        user = self.request.user.userprofile
        qs = self.queryset
        if not user.is_view_all():
            qs = qs.filter(
                project_id__in=user.get_projects(),
                computer_id__in=user.get_computers()
            )

        return qs


class NotificationViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = models.Notification.objects.all()
    serializer_class = serializers.NotificationSerializer
    filter_class = NotificationFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('-created_at',)

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return serializers.NotificationWriteSerializer

        return serializers.NotificationSerializer


class PackageViewSet(viewsets.ModelViewSet):
    queryset = models.Package.objects.all()
    serializer_class = serializers.PackageSerializer
    filter_class = PackageFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('name',)

    def get_queryset(self):
        user = self.request.user.userprofile
        qs = self.queryset
        if not user.is_view_all():
            qs = qs.filter(project__in=user.get_projects())

        return qs

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.PackageWriteSerializer

        return serializers.PackageSerializer

    @list_route(methods=['get'])
    def orphan(self, request):
        """
        Returns packages that are not in any deployment
        """
        serializer = serializers.PackageSerializer(
            models.Package.objects.filter(deployment__id=None),
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class PlatformViewSet(viewsets.ModelViewSet):
    queryset = models.Platform.objects.all()
    serializer_class = serializers.PlatformSerializer
    ordering_fields = '__all__'
    ordering = ('name',)

    def get_queryset(self):
        user = self.request.user.userprofile
        qs = self.queryset
        if not user.is_view_all():
            qs = qs.filter(project__in=user.get_projects()).distinct()

        return qs


class PmsViewSet(viewsets.ModelViewSet):
    queryset = models.Pms.objects.all()
    serializer_class = serializers.PmsSerializer
    ordering_fields = '__all__'
    ordering = ('name',)


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = models.Property.objects.all()
    serializer_class = serializers.PropertySerializer
    filter_class = PropertyFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('prefix', 'name',)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.PropertyWriteSerializer

        return serializers.PropertySerializer


class DeploymentViewSet(viewsets.ModelViewSet):
    queryset = models.Deployment.objects.all()
    serializer_class = serializers.DeploymentSerializer
    filter_class = DeploymentFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('-start_date',)

    def get_queryset(self):
        user = self.request.user.userprofile
        qs = self.queryset
        if not user.is_view_all():
            qs = qs.filter(project__in=user.get_projects())
            if user.domain_preference:
                qs = qs.filter(domain=user.domain_preference)

        return qs

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.DeploymentWriteSerializer

        return serializers.DeploymentSerializer

    @detail_route(methods=['get'])
    def metadata(self, request, pk=None):
        get_object_or_404(models.Deployment, pk=pk)
        ret = create_repository_metadata(pk)

        return Response(
            {'detail': ret},
            status=status.HTTP_200_OK
        )


class ScheduleDelayViewSet(viewsets.ModelViewSet):
    queryset = models.ScheduleDelay.objects.all()
    serializer_class = serializers.ScheduleDelaySerializer
    filter_class = ScheduleDelayFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('delay',)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.ScheduleDelayWriteSerializer

        return serializers.ScheduleDelaySerializer


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = models.Schedule.objects.all()
    serializer_class = serializers.ScheduleSerializer
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('name',)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.ScheduleWriteSerializer

        return serializers.ScheduleSerializer


class StatusLogViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = models.StatusLog.objects.all()
    serializer_class = serializers.StatusLogSerializer
    filter_class = StatusLogFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('-created_at',)

    def get_queryset(self):
        user = self.request.user.userprofile
        qs = self.queryset
        if not user.is_view_all():
            qs = qs.filter(computer_id__in=user.get_computers())

        return qs


class StoreViewSet(viewsets.ModelViewSet):
    queryset = models.Store.objects.all()
    serializer_class = serializers.StoreSerializer
    filter_class = StoreFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('name',)

    def get_queryset(self):
        user = self.request.user.userprofile
        qs = self.queryset
        if not user.is_view_all():
            qs = qs.filter(project__in=user.get_projects())

        return qs

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.StoreWriteSerializer

        return serializers.StoreSerializer


class SynchronizationViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = models.Synchronization.objects.all()
    serializer_class = serializers.SynchronizationSerializer
    filter_class = SynchronizationFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('-created_at',)

    def get_queryset(self):
        user = self.request.user.userprofile
        qs = self.queryset
        if not user.is_view_all():
            qs = qs.filter(
                project_id__in=user.get_projects(),
                computer_id__in=user.get_computers()
            )

        return qs


class UserViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    ordering_fields = '__all__'
    ordering = ('name',)

    def get_queryset(self):
        user = self.request.user.userprofile
        qs = self.queryset
        if not user.is_view_all():
            qs = qs.filter(computer__in=user.get_computers())

        return qs


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    filter_class = ProjectFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('name',)

    def get_queryset(self):
        user = self.request.user.userprofile
        qs = self.queryset
        if not user.is_view_all():
            qs = qs.filter(id__in=user.get_projects())

        return qs

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.ProjectWriteSerializer

        return serializers.ProjectSerializer


class DomainViewSet(viewsets.ModelViewSet):
    queryset = models.Domain.objects.all()
    serializer_class = serializers.DomainSerializer
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('name',)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.DomainWriteSerializer

        return serializers.DomainSerializer


class ScopeViewSet(viewsets.ModelViewSet):
    queryset = models.Scope.objects.all()
    serializer_class = serializers.ScopeSerializer
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('name',)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.ScopeWriteSerializer

        return serializers.ScopeSerializer


class ConnectionViewSet(viewsets.ModelViewSet):
    queryset = models.DeviceConnection.objects.all()
    serializer_class = serializers.ConnectionSerializer
    ordering_fields = '__all__'
    ordering = ('id',)


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = models.Device.objects.all()
    serializer_class = serializers.DeviceSerializer
    filter_class = DeviceFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('name',)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.DeviceWriteSerializer

        return serializers.DeviceSerializer


class DriverViewSet(viewsets.ModelViewSet):
    queryset = models.DeviceDriver.objects.all()
    serializer_class = serializers.DriverSerializer
    filter_class = DriverFilter
    ordering_fields = '__all__'
    ordering = ('name',)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.DriverWriteSerializer

        return serializers.DriverSerializer


class FeatureViewSet(viewsets.ModelViewSet):
    queryset = models.DeviceFeature.objects.all()
    serializer_class = serializers.FeatureSerializer
    ordering_fields = '__all__'
    ordering = ('name',)


class LogicalViewSet(viewsets.ModelViewSet):
    queryset = models.DeviceLogical.objects.all()
    serializer_class = serializers.LogicalSerializer
    ordering_fields = '__all__'
    ordering = ('device__name',)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.LogicalWriteSerializer

        return serializers.LogicalSerializer

    @list_route(methods=['get'])
    def availables(self, request):
        """
        :param request:
            cid (computer Id) int,
            q string (name or data contains...),
            page int
        :return: DeviceLogicalSerializer set
        """
        computer = get_object_or_404(models.Computer, pk=request.GET.get('cid', 0))
        query = request.GET.get('q', '')

        results = models.DeviceLogical.objects.filter(
            device__available_for_attributes__in=computer.sync_attributes.values_list('id', flat=True)
        ).order_by('device__name', 'feature__name')
        if query:
            results = results.filter(Q(device__name__icontains=query) | Q(device__data__icontains=query))

        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = models.DeviceManufacturer.objects.all()
    serializer_class = serializers.ManufacturerSerializer
    ordering_fields = '__all__'
    ordering = ('name',)


class ModelViewSet(viewsets.ModelViewSet):
    queryset = models.DeviceModel.objects.all()
    serializer_class = serializers.ModelSerializer
    ordering_fields = '__all__'
    ordering = ('name',)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.ModelWriteSerializer

        return serializers.ModelSerializer


class TypeViewSet(viewsets.ModelViewSet):
    queryset = models.DeviceType.objects.all()
    serializer_class = serializers.TypeSerializer
    ordering_fields = '__all__'
    ordering = ('name',)
