# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, exceptions, status, mixins, filters
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework_filters import backends

from .. import models, serializers
from ..filters import ComputerFilter
from ..permissions import PublicPermission, IsAdminOrIsSelf


class ComputerViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Computer.objects.all()
    serializer_class = serializers.ComputerSerializer
    filter_class = ComputerFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    permission_classes = (PublicPermission,)

    @detail_route(methods=['post'], permission_classes=[IsAdminOrIsSelf])
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

    @detail_route(methods=['post'], permission_classes=[IsAdminOrIsSelf])
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
