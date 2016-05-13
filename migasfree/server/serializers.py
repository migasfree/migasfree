# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from . import models


class AttributeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Attribute
        fields = ('id', 'value')


class AttributeSerializer(serializers.ModelSerializer):
    total_computers = serializers.SerializerMethodField()

    def get_total_computers(self, obj):
        return obj.total_computers()

    class Meta:
        model = models.Attribute
        fields = '__all__'


class CheckingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Checking
        fields = '__all__'


class ComputerInfoSerializer(serializers.ModelSerializer):
    cid_description = serializers.SerializerMethodField()

    def get_cid_description(self, obj):
        return obj.get_cid_description()

    class Meta:
        model = models.Computer
        fields = ('id', 'cid_description')


class VersionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Version
        fields = ('id', 'name')


class ComputerSerializer(serializers.ModelSerializer):
    version = VersionInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.Computer
        fields = (
            'id', 'uuid', 'name', 'version', 'ip',
            'status', 'product', 'machine',
            'mac_address', 'cpu', 'disks', 'storage', 'ram',
            'dateinput', 'datehardware', 'datelastupdate',
        )


class ErrorSerializer(serializers.ModelSerializer):
    version = VersionInfoSerializer(many=False, read_only=True)
    computer = ComputerInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.Error
        fields = '__all__'


class FaultDefinitionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FaultDef
        fields = ('id', 'name')


class UserProfileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = ('id', 'username')


class FaultDefinitionSerializer(serializers.ModelSerializer):
    language = serializers.SerializerMethodField()
    attributes = AttributeInfoSerializer(many=True, read_only=True)
    users = UserProfileInfoSerializer(many=True, read_only=True)

    def get_language(self, obj):
        return obj.get_language_display()

    class Meta:
        model = models.FaultDef
        fields = '__all__'


class FaultSerializer(serializers.ModelSerializer):
    version = VersionInfoSerializer(many=False, read_only=True)
    computer = ComputerInfoSerializer(many=False, read_only=True)
    faultdef = FaultDefinitionInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.Fault
        fields = '__all__'


class MigrationSerializer(serializers.ModelSerializer):
    version = VersionInfoSerializer(many=False, read_only=True)
    computer = ComputerInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.Migration
        fields = '__all__'


class NodeSerializer(serializers.ModelSerializer):
    computer = ComputerInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.HwNode
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Notification
        fields = '__all__'


class PackageInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Package
        fields = ('id', 'name')


class StoreInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Store
        fields = ('id', 'name')


class PackageSerializer(serializers.ModelSerializer):
    version = VersionInfoSerializer(many=False, read_only=True)
    store = StoreInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.Package
        fields = '__all__'


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Platform
        fields = ('id', 'name')


class PmsInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pms
        fields = ('id', 'name')


class PmsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pms
        fields = ('id', 'name', 'slug', 'createrepo', 'info')


class PropertySerializer(serializers.ModelSerializer):
    language = serializers.SerializerMethodField()

    def get_language(self, obj):
        return obj.get_language_display()

    class Meta:
        model = models.Property
        fields = '__all__'


class ScheduleInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Schedule
        fields = ('id', 'name')


class RepositorySerializer(serializers.ModelSerializer):
    version = VersionInfoSerializer(many=False, read_only=True)
    schedule = ScheduleInfoSerializer(many=False, read_only=True)
    packages = PackageInfoSerializer(many=True, read_only=True)
    attributes = AttributeInfoSerializer(many=True, read_only=True)
    excludes = AttributeInfoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Repository
        fields = '__all__'


class ScheduleDelaySerializer(serializers.ModelSerializer):
    attributes = AttributeSerializer(many=True, read_only=True)
    total_computers = serializers.SerializerMethodField()

    def get_total_computers(self, obj):
        return obj.total_computers()

    class Meta:
        model = models.ScheduleDelay
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    delays = ScheduleDelaySerializer(many=True, read_only=True)

    class Meta:
        model = models.Schedule
        fields = ('id', 'name', 'description', 'delays')  # FIXME delays???


class StoreSerializer(serializers.ModelSerializer):
    version = VersionInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.Store
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'


class VersionSerializer(serializers.ModelSerializer):
    platform = PlatformSerializer(many=False, read_only=True)
    pms = PmsInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.Version
        fields = '__all__'
