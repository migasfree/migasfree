# -*- coding: utf-8 -*-

from rest_framework import serializers

from ..server.utils import to_list
from ..server.serializers import AttributeInfoSerializer

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
        if 'packages_to_install' in data:
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


class ApplicationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Application
        fields = ['id', 'name']


class ApplicationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Application
        fields = '__all__'


class ApplicationSerializer(serializers.ModelSerializer):
    level = LevelSerializer(many=False, read_only=True)
    category = CategorySerializer(many=False, read_only=True)
    packages_by_project = PackagesByProjectSerializer(many=True, read_only=True)
    available_for_attributes = AttributeInfoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Application
        fields = '__all__'


class PolicyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Policy
        fields = ['id', 'name']


class PolicyWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Policy
        fields = '__all__'


class PolicySerializer(serializers.ModelSerializer):
    included_attributes = AttributeInfoSerializer(many=True, read_only=True)
    excluded_attributes = AttributeInfoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Policy
        fields = '__all__'


class PolicyGroupWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PolicyGroup
        fields = '__all__'


class PolicyGroupSerializer(serializers.ModelSerializer):
    policy = PolicyInfoSerializer(many=False, read_only=True)
    applications = ApplicationInfoSerializer(many=True, read_only=True)
    included_attributes = AttributeInfoSerializer(many=True, read_only=True)
    excluded_attributes = AttributeInfoSerializer(many=True, read_only=True)

    class Meta:
        model = models.PolicyGroup
        fields = '__all__'
