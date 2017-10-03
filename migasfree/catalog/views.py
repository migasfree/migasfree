# -*- coding: utf-8 -*-

from rest_framework import viewsets, mixins, filters, status
from rest_framework_filters import backends
from rest_framework.decorators import list_route
from rest_framework.response import Response

from migasfree.server.permissions import PublicPermission
from . import models, serializers
from .filters import ApplicationFilter


class ApplicationViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = models.Application.objects.all()
    serializer_class = serializers.ApplicationSerializer
    filter_class = ApplicationFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    permission_classes = (PublicPermission,)

    @list_route(methods=['get'])
    def levels(self, request):
        return Response(
            dict(models.Application.LEVELS),
            status=status.HTTP_200_OK
        )

    @list_route(methods=['get'])
    def categories(self, request):
        return Response(
            dict(models.Application.CATEGORIES),
            status=status.HTTP_200_OK
        )
