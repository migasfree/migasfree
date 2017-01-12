# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from . import models, tasks


class AttributeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Attribute
        fields = ('id', 'value')


class PropertyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Property
        fields = ('id', 'prefix')


class AttributeSerializer(serializers.ModelSerializer):
    total_computers = serializers.SerializerMethodField()
    property_att = PropertyInfoSerializer(many=False, read_only=True)

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


class RepositoryWriteSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        deploy = super(RepositoryWriteSerializer, self).create(validated_data)
        tasks.create_physical_repository(deploy)
        return deploy

    def update(self, instance, validated_data):
        old_obj = self.Meta.model.objects.get(id=instance.id)
        old_pkgs = sorted(
            old_obj.packages.values_list('id', flat=True)
        )
        old_name = old_obj.name

        # https://github.com/tomchristie/django-rest-framework/issues/2442
        instance = super(RepositoryWriteSerializer, self).update(
            instance, validated_data
        )
        new_pkgs = sorted(
            instance.packages.values_list('id', flat=True)
        )

        if cmp(old_pkgs, new_pkgs) != 0 or old_name != validated_data['name']:
            tasks.create_physical_repository(instance)

            if old_name != validated_data['name']:
                tasks.remove_physical_repository(
                    {}, instance, old_name
                )

        return instance

    def _validate_active_computers(self, att_list):
        for attribute in att_list:
            if attribute.property_att.prefix == 'CID':
                computer = models.Computer.objects.get(pk=int(attribute.value))
                if computer.status not in models.Computer.ACTIVE_STATUS:
                    raise serializers.ValidationError(
                        _('It is not possible to assign an inactive computer (%s) as an attribute')
                        % computer.__str__()
                    )

    def validate(self, data):
        for item in data.get('packages', []):
            if item.version.id != data['version'].id:
                raise serializers.ValidationError(
                    _('Package %s must belong to the version %s') % (
                        item, data['version']
                    )
                )

        self._validate_active_computers(data.get('attributes', []))
        self._validate_active_computers(data.get('excludes', []))

        return data

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


class DeviceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Device
        fields = ('id', 'name')


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceFeature
        fields = '__all__'


class LogicalSerializer(serializers.ModelSerializer):
    device = DeviceInfoSerializer(many=False, read_only=True)
    feature = FeatureSerializer(many=False, read_only=True)

    class Meta:
        model = models.DeviceLogical
        fields = '__all__'


class UpdateSerializer(serializers.ModelSerializer):
    version = VersionInfoSerializer(many=False, read_only=True)
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = models.Update
        fields = '__all__'


class StatusLogSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = models.StatusLog
        fields = '__all__'


class ComputerSyncSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    attributes = AttributeSerializer(many=True, read_only=True)

    class Meta:
        model = models.Login
        fields = ('date', 'user', 'attributes')
