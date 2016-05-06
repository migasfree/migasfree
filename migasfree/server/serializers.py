# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from . import models


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Version
        fields = ('id', 'name')


class ComputerSerializer(serializers.ModelSerializer):
    version = VersionSerializer(many=False, read_only=True)

    class Meta:
        model = models.Computer
        fields = (
            'id', 'uuid', 'name', 'version', 'ip',
            'status', 'product', 'machine',
            'mac_address', 'cpu', 'disks', 'storage', 'ram',
            'dateinput', 'datehardware', 'datelastupdate',
        )
