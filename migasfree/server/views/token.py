# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, exceptions, status, mixins, filters
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework_filters import backends

from .. import models, serializers
from ..filters import (
    ComputerFilter, StoreFilter, PropertyFilter,
    VersionFilter, AttributeFilter, PackageFilter,
    RepositoryFilter, ErrorFilter, FaultDefinitionFilter,
    FaultFilter, NotificationFilter, MigrationFilter,
    NodeFilter, CheckingFilter,
)
# from ..permissions import PublicPermission, IsAdminOrIsSelf


class AttributeViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Attribute.objects.all()
    serializer_class = serializers.AttributeSerializer
    filter_class = AttributeFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)


class CheckingViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Checking.objects.all()
    serializer_class = serializers.CheckingSerializer
    filter_class = CheckingFilter
    ordering_fields = '__all__'
    ordering = ('id',)


class ComputerViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Computer.objects.all()
    serializer_class = serializers.ComputerSerializer
    filter_class = ComputerFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)

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
        print request.auth

        ret = computer.change_status(request.data.get('status'))
        if not ret:
            raise exceptions.ParseError(
                _('Status must have one of the values: %s') % (
                    dict(models.Computer.STATUS_CHOICES).keys()
                )
            )

        serializer = serializers.ComputerSerializer(computer)
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


class ErrorViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Error.objects.all()
    serializer_class = serializers.ErrorSerializer
    filter_class = ErrorFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('-date',)


class FaultDefinitionViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.FaultDef.objects.all()
    serializer_class = serializers.FaultDefinitionSerializer
    filter_class = FaultDefinitionFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)


class FaultViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Fault.objects.all()
    serializer_class = serializers.FaultSerializer
    filter_class = FaultFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('-date',)


class HardwareComputerViewSet(viewsets.ViewSet):
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


class MigrationViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Migration.objects.all()
    serializer_class = serializers.MigrationSerializer
    filter_class = MigrationFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('-date',)


class NotificationViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Notification.objects.all()
    serializer_class = serializers.NotificationSerializer
    filter_class = NotificationFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('-date',)


class PackageViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Package.objects.all()
    serializer_class = serializers.PackageSerializer
    filter_class = PackageFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)

    @list_route(methods=['get'])
    def orphaned(self, request):
        """
        Returns packages that are not in any deployment
        """
        serializer = serializers.PackageSerializer(
            models.Package.objects.filter(repository__id=None),
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class PlatformViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Platform.objects.all()
    serializer_class = serializers.PlatformSerializer


class PmsViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Pms.objects.all()
    serializer_class = serializers.PmsSerializer


class PropertyViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Property.objects.all()
    serializer_class = serializers.PropertySerializer
    filter_class = PropertyFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)


class RepositoryViewSet(viewsets.ModelViewSet):
    queryset = models.Repository.objects.all()
    serializer_class = serializers.RepositorySerializer
    filter_class = RepositoryFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    ordering_fields = '__all__'
    ordering = ('-date',)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return serializers.RepositoryWriteSerializer

        return serializers.RepositorySerializer


class ScheduleViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Schedule.objects.all()
    serializer_class = serializers.ScheduleSerializer


class StoreViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Store.objects.all()
    serializer_class = serializers.StoreSerializer
    filter_class = StoreFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)


class UserViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    ordering_fields = '__all__'
    ordering = ('name',)


class VersionViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Version.objects.all()
    serializer_class = serializers.VersionSerializer
    filter_class = VersionFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
