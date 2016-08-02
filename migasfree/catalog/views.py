# -*- coding: utf-8 -*-

from rest_framework import viewsets, mixins, filters
from rest_framework_filters import backends

from migasfree.server.permissions import PublicPermission
from . import models, serializers
from .filters import ApplicationFilter


class ApplicationViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Application.objects.all()
    serializer_class = serializers.ApplicationSerializer
    filter_class = ApplicationFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    permission_classes = (PublicPermission,)
