# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from migasfree.server.utils import to_list
from . import models


class LevelSerializer(serializers.Serializer):
    def to_representation(self, obj):
        return {
            'id': obj,
            'name': dict(models.Application.LEVELS)[obj]
        }


class CategorySerializer(serializers.Serializer):
    def to_representation(self, obj):
        return {
            'id': obj,
            'name': dict(models.Application.CATEGORIES)[obj]
        }


class PackagesByProjectWriteSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        """
        :param data: {
            'project': 17,
            'application': 1,
            'packages_to_install': ['one', 'two']
        }
        :return: PackagesByProject object
        """
        if 'packages_to_install' not in data:
            msg = _('Incorrect data structure. Missing %s.')
            raise serializers.ValidationError(msg % 'packages_to_install')

        data['packages_to_install'] = '\n'.join(data.get('packages_to_install', []))
        return super(PackagesByProjectWriteSerializer, self).to_internal_value(data)

    class Meta:
        model = models.PackagesByProject
        fields = '__all__'


class PackagesByProjectSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.id,
            'application': obj.application.id,
            'project': {
                'id': obj.project.id,
                'name': obj.project.name
            },
            'packages_to_install': to_list(obj.packages_to_install)
        }

    class Meta:
        model = models.PackagesByProject
        fields = '__all__'


class ApplicationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Application
        fields = '__all__'


class ApplicationSerializer(serializers.ModelSerializer):
    level = LevelSerializer(many=False, read_only=True)
    category = CategorySerializer(many=False, read_only=True)
    packages_by_project = PackagesByProjectSerializer(many=True, read_only=True)

    class Meta:
        model = models.Application
        fields = '__all__'
