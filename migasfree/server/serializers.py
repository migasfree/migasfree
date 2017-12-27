# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from . import models, tasks
from .utils import to_list


class AttributeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Attribute
        fields = ('id', 'value')


class AttributeSetSerializer(serializers.ModelSerializer):
    included_attributes = AttributeInfoSerializer(many=True, read_only=True)
    excluded_attributes = AttributeInfoSerializer(many=True, read_only=True)

    class Meta:
        model = models.AttributeSet
        fields = '__all__'


class AttributeSetWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AttributeSet
        fields = '__all__'


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


class AttributeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Attribute
        fields = ('description',)


class ComputerInfoSerializer(serializers.ModelSerializer):
    cid_description = serializers.SerializerMethodField()

    def get_cid_description(self, obj):
        return obj.get_cid_description()

    class Meta:
        model = models.Computer
        fields = ('id', 'cid_description')


class ProjectInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = ('id', 'name')


class ComputerSerializer(serializers.ModelSerializer):
    project = ProjectInfoSerializer(many=False, read_only=True)
    software_inventory = serializers.HyperlinkedIdentityField(
        view_name='computer-software/inventory'
    )
    software_history = serializers.HyperlinkedIdentityField(
        view_name='computer-software/history'
    )
    tags = AttributeInfoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Computer
        fields = (
            'id', 'uuid', 'name', 'fqdn', 'project', 'comment',
            'ip_address', 'forwarded_ip_address',
            'status', 'product', 'machine',
            'mac_address', 'cpu', 'disks', 'storage', 'ram',
            'created_at', 'last_hardware_capture', 'sync_end_date',
            'software_inventory', 'software_history', 'tags',
        )


class ComputerWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Computer
        fields = (
            'name', 'last_hardware_capture',
            'status', 'comment', 'tags',
            'default_logical_device',
        )


class ErrorSerializer(serializers.ModelSerializer):
    project = ProjectInfoSerializer(many=False, read_only=True)
    computer = ComputerInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.Error
        fields = '__all__'


class ErrorWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Error
        fields = ('checked',)


class FaultDefinitionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FaultDefinition
        fields = ('id', 'name')


class UserProfileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = ('id', 'username')


class FaultDefinitionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FaultDefinition
        fields = '__all__'


class FaultDefinitionSerializer(serializers.ModelSerializer):
    language = serializers.SerializerMethodField()
    included_attributes = AttributeInfoSerializer(many=True, read_only=True)
    excluded_attributes = AttributeInfoSerializer(many=True, read_only=True)
    users = UserProfileInfoSerializer(many=True, read_only=True)

    def get_language(self, obj):
        return obj.get_language_display()

    class Meta:
        model = models.FaultDefinition
        fields = '__all__'


class FaultSerializer(serializers.ModelSerializer):
    project = ProjectInfoSerializer(many=False, read_only=True)
    computer = ComputerInfoSerializer(many=False, read_only=True)
    fault_definition = FaultDefinitionInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.Fault
        fields = '__all__'


class FaultWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Fault
        fields = ('checked',)


class MigrationSerializer(serializers.ModelSerializer):
    project = ProjectInfoSerializer(many=False, read_only=True)
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


class NotificationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Notification
        fields = ('checked',)


class PackageInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Package
        fields = ('id', 'name')


class StoreInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Store
        fields = ('id', 'name')


class PackageWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Package
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):
    project = ProjectInfoSerializer(many=False, read_only=True)
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


class PropertyWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Property
        fields = '__all__'


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


class DeploymentSerializer(serializers.ModelSerializer):
    project = ProjectInfoSerializer(many=False, read_only=True)
    schedule = ScheduleInfoSerializer(many=False, read_only=True)
    available_packages = PackageInfoSerializer(many=True, read_only=True)
    included_attributes = AttributeInfoSerializer(many=True, read_only=True)
    excluded_attributes = AttributeInfoSerializer(many=True, read_only=True)

    packages_to_install = serializers.SerializerMethodField()
    packages_to_remove = serializers.SerializerMethodField()
    default_preincluded_packages = serializers.SerializerMethodField()
    default_included_packages = serializers.SerializerMethodField()
    default_excluded_packages = serializers.SerializerMethodField()

    def get_packages_to_install(self, obj):
        return to_list(obj.packages_to_install)

    def get_packages_to_remove(self, obj):
        return to_list(obj.packages_to_remove)

    def get_default_preincluded_packages(self, obj):
        return to_list(obj.default_preincluded_packages)

    def get_default_included_packages(self, obj):
        return to_list(obj.default_included_packages)

    def get_default_excluded_packages(self, obj):
        return to_list(obj.default_excluded_packages)

    class Meta:
        model = models.Deployment
        fields = '__all__'


class DeploymentWriteSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        """
        :param data: {
            "enabled": true,
            "project": id,
            "name": "string",
            "comment": "string",
            "available_packages": ["string", ...],
            "start_date": "string",
            "packages_to_install": [],
            "packages_to_remove": [],
            "default_preincluded_packages": [],
            "default_included_packages": [],
            "default_excluded_packages": [],
            "schedule": id,
            "included_attributes": [id1, id2, ...],
            "excluded_attributes": [id1, ...]
        }
        :return: Deployment object
        """
        if 'packages_to_install' in data:
            data['packages_to_install'] = '\n'.join(data.get('packages_to_install', []))

        if 'packages_to_remove' in data:
            data['packages_to_remove'] = '\n'.join(data.get('packages_to_remove', []))

        if 'default_preincluded_packages' in data:
            data['default_preincluded_packages'] = '\n'.join(data.get('default_preincluded_packages', []))

        if 'default_included_packages' in data:
            data['default_included_packages'] = '\n'.join(data.get('default_included_packages', []))

        if 'default_excluded_packages' in data:
            data['default_excluded_packages'] = '\n'.join(data.get('default_excluded_packages', []))

        return super(DeploymentWriteSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        deploy = super(DeploymentWriteSerializer, self).create(validated_data)
        tasks.create_repository_metadata(deploy)
        return deploy

    def update(self, instance, validated_data):
        old_obj = self.Meta.model.objects.get(id=instance.id)
        old_pkgs = sorted(
            old_obj.available_packages.values_list('id', flat=True)
        )
        old_name = old_obj.name

        # https://github.com/tomchristie/django-rest-framework/issues/2442
        instance = super(DeploymentWriteSerializer, self).update(
            instance, validated_data
        )
        new_pkgs = sorted(
            instance.available_packages.values_list('id', flat=True)
        )

        if cmp(old_pkgs, new_pkgs) != 0 or old_name != validated_data['name']:
            tasks.create_repository_metadata(instance)

            if old_name != validated_data['name']:
                tasks.remove_repository_metadata(
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
                        % computer
                    )

    def validate(self, data):
        for item in data.get('packages', []):
            if item.project.id != data['project'].id:
                raise serializers.ValidationError(
                    _('Package %s must belong to the project %s') % (
                        item, data['project']
                    )
                )

        self._validate_active_computers(data.get('included_attributes', []))
        self._validate_active_computers(data.get('excluded_attributes', []))

        return data

    class Meta:
        model = models.Deployment
        fields = '__all__'


class ScheduleDelayWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ScheduleDelay
        fields = '__all__'


class ScheduleDelaySerializer(serializers.ModelSerializer):
    attributes = AttributeSerializer(many=True, read_only=True)
    total_computers = serializers.SerializerMethodField()

    def get_total_computers(self, obj):
        return obj.total_computers()

    class Meta:
        model = models.ScheduleDelay
        fields = '__all__'


class ScheduleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Schedule
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    delays = ScheduleDelaySerializer(many=True, read_only=True)

    class Meta:
        model = models.Schedule
        fields = ('id', 'name', 'description', 'delays')


class StoreWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Store
        fields = '__all__'


class StoreSerializer(serializers.ModelSerializer):
    project = ProjectInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.Store
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'


class ProjectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    platform = PlatformSerializer(many=False, read_only=True)
    pms = PmsInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.Project
        fields = '__all__'


class SynchronizationSerializer(serializers.ModelSerializer):
    project = ProjectInfoSerializer(many=False, read_only=True)
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = models.Synchronization
        fields = '__all__'


class StatusLogSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = models.StatusLog
        fields = '__all__'


class ComputerSyncSerializer(serializers.ModelSerializer):
    sync_user = UserSerializer(many=False, read_only=True)
    sync_attributes = AttributeSerializer(many=True, read_only=True)

    class Meta:
        model = models.Computer
        fields = ('sync_start_date', 'sync_end_date', 'sync_user', 'sync_attributes')


class ConnectionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceConnection
        fields = ('id', 'name')


class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceConnection
        fields = '__all__'


class ModelInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceModel
        fields = ('id', 'name')


class DeviceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Device
        fields = ('id', 'name')


class DeviceWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Device
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    connection = ConnectionInfoSerializer(many=False, read_only=True)
    model = ModelInfoSerializer(many=False, read_only=True)
    available_for_attributes = AttributeInfoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Device
        fields = '__all__'


class FeatureInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceFeature
        fields = ('id', 'name')


class DriverWriteSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        if 'packages_to_install' in data:
            data['packages_to_install'] = '\n'.join(data.get('packages_to_install', []))

        return super(DriverWriteSerializer, self).to_internal_value(data)

    class Meta:
        model = models.DeviceDriver
        fields = '__all__'


class DriverSerializer(serializers.ModelSerializer):
    model = ModelInfoSerializer(many=False, read_only=True)
    project = ProjectInfoSerializer(many=False, read_only=True)
    feature = FeatureInfoSerializer(many=False, read_only=True)
    packages_to_install = serializers.SerializerMethodField()

    def get_packages_to_install(self, obj):
        return to_list(obj.packages_to_install)

    class Meta:
        model = models.DeviceDriver
        fields = '__all__'


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


class LogicalWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceLogical
        fields = '__all__'


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceManufacturer
        fields = '__all__'


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceType
        fields = '__all__'


class ModelWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceModel
        fields = '__all__'


class ModelSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerSerializer(many=False, read_only=True)
    connections = ConnectionInfoSerializer(many=True, read_only=True)
    device_type = TypeSerializer(many=False, read_only=True)

    class Meta:
        model = models.DeviceModel
        fields = '__all__'
