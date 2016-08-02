# -*- coding: utf-8 -*-

from rest_framework import serializers

from migasfree.server.serializers import VersionInfoSerializer
from . import models


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.ChoiceField(choices=models.Application.CATEGORIES)
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.Application
        fields = ('id', 'name')

    def get_name(self, obj):
        return obj.get_category_display()


class ApplicationSerializer(serializers.ModelSerializer):
    version = VersionInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.Application
        fields = '__all__'

    def to_representation(self, obj):
        return {
            'id': obj.id,
            'name': obj.name,
            'description': obj.description,
            'packages_to_install': obj.packages_to_install,
            'score': obj.score,
            'icon': self.context['request'].build_absolute_uri(obj.icon.url),
            'level':  obj.level,
            'version': {
                'id': obj.version.id,
                'name': obj.version.name
            },
            'category': {
                'id': obj.category,
                'name': obj.get_category_display()
            }
        }
