# -*- coding: utf-8 -*-

from past.builtins import cmp

from django.contrib.auth.models import Group, Permission
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_auth.serializers import UserDetailsSerializer

from . import models, tasks
from .utils import to_list


class PropertyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Property
        fields = ('id', 'prefix')


class AttributeInfoSerializer(serializers.ModelSerializer):
    property_att = PropertyInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.Attribute
        fields = ('id', 'property_att', 'value')


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


class AttributeSerializer(serializers.ModelSerializer):
    total_computers = serializers.SerializerMethodField()
    property_att = PropertyInfoSerializer(many=False, read_only=True)

    def get_total_computers(self, obj):
        if self.context.get('request'):
            return obj.total_computers(user=self.context['request'].user)

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
        view_name='computer-software_inventory',
    )
    software_history = serializers.HyperlinkedIdentityField(
        view_name='computer-software_history',
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
    def is_valid(self, raise_exception=False):
        data = self.get_initial()
        if data.get('tags') and data.get('tags')[0] == '':
            self.instance.tags.clear()
            del self.fields['tags']

        return super(ComputerWriteSerializer, self).is_valid(raise_exception)

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


class InternalSourceSerializer(DeploymentSerializer):
    available_packages = PackageInfoSerializer(many=True, read_only=True)

    class Meta:
        model = models.InternalSource
        fields = (
            'enabled', 'project', 'domain', 'name', 'comment',
            'available_packages',
            'included_attributes', 'excluded_attributes',
            'packages_to_install', 'packages_to_remove',
            'default_preincluded_packages', 'default_included_packages', 'default_excluded_packages',
            'schedule', 'start_date'
        )


class ExternalSourceSerializer(DeploymentSerializer):
    class Meta:
        model = models.ExternalSource
        fields = (
            'enabled', 'project', 'domain', 'name', 'comment',
            'included_attributes', 'excluded_attributes',
            'packages_to_install', 'packages_to_remove',
            'default_preincluded_packages', 'default_included_packages', 'default_excluded_packages',
            'schedule', 'start_date',
            'base_url', 'options', 'suite', 'components', 'frozen', 'expire'
        )


class DeploymentWriteSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        """
        :param data: {
            "enabled": true,
            "project": id,
            "domain": id,
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


class InternalSourceWriteSerializer(DeploymentWriteSerializer):
    def create(self, validated_data):
        deploy = super(InternalSourceWriteSerializer, self).create(validated_data)
        tasks.create_repository_metadata(deploy)
        return deploy

    def update(self, instance, validated_data):
        old_obj = self.Meta.model.objects.get(id=instance.id)
        old_pkgs = sorted(
            old_obj.available_packages.values_list('id', flat=True)
        )
        old_name = old_obj.name

        # https://github.com/tomchristie/django-rest-framework/issues/2442
        instance = super(InternalSourceWriteSerializer, self).update(
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

    class Meta:
        model = models.InternalSource
        fields = (
            'enabled', 'project', 'domain', 'name', 'comment',
            'available_packages',
            'included_attributes', 'excluded_attributes',
            'packages_to_install', 'packages_to_remove',
            'default_preincluded_packages', 'default_included_packages', 'default_excluded_packages',
            'schedule', 'start_date'
        )


class ExternalSourceWriteSerializer(DeploymentWriteSerializer):
    class Meta:
        model = models.ExternalSource
        fields = (
            'enabled', 'project', 'domain', 'name', 'comment',
            'included_attributes', 'excluded_attributes',
            'packages_to_install', 'packages_to_remove',
            'default_preincluded_packages', 'default_included_packages', 'default_excluded_packages',
            'schedule', 'start_date',
            'base_url', 'options', 'suite', 'components', 'frozen', 'expire'
        )


class ScheduleDelayWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ScheduleDelay
        fields = '__all__'


class ScheduleDelaySerializer(serializers.ModelSerializer):
    attributes = AttributeSerializer(many=True, read_only=True)
    total_computers = serializers.SerializerMethodField()

    def get_total_computers(self, obj):
        if self.context.get('request'):
            return obj.total_computers(user=self.context['request'].user)

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

    def __init__(self, *args, **kwargs):
        super(ComputerSyncSerializer, self).__init__(*args, **kwargs)

        context = kwargs.get('context', None)
        if context:
            request = kwargs['context']['request']
            self.sync_attributes = AttributeSerializer(many=True, read_only=True, context={'request': request})

    class Meta:
        model = models.Computer
        fields = ('sync_start_date', 'sync_end_date', 'sync_user', 'sync_attributes')


class DomainInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Domain
        fields = ('id', 'name')


class DomainSerializer(serializers.ModelSerializer):
    included_attributes = AttributeInfoSerializer(many=True, read_only=True)
    excluded_attributes = AttributeInfoSerializer(many=True, read_only=True)
    tags = AttributeInfoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Domain
        fields = '__all__'


class DomainWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Domain
        fields = '__all__'


class ScopeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Scope
        fields = ('id', 'name')


class ScopeSerializer(serializers.ModelSerializer):
    included_attributes = AttributeInfoSerializer(many=True, read_only=True)
    excluded_attributes = AttributeInfoSerializer(many=True, read_only=True)
    user = UserProfileInfoSerializer(many=False, read_only=True)
    domain = DomainInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.Scope
        fields = '__all__'


class ScopeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Scope
        fields = '__all__'


class ConnectionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceConnection
        fields = ('id', 'name')


class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceConnection
        fields = '__all__'


class ManufacturerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceManufacturer
        fields = ('id', 'name')


class ModelInfoSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerInfoSerializer(many=False, read_only=True)

    class Meta:
        model = models.DeviceModel
        fields = ('id', 'name', 'manufacturer')


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


class LogicalInfoSerializer(serializers.ModelSerializer):
    device = DeviceInfoSerializer(many=False, read_only=True)
    feature = FeatureSerializer(many=False, read_only=True)

    class Meta:
        model = models.DeviceLogical
        fields = ('id', 'device', 'feature')


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


class ComputerDevicesSerializer(serializers.ModelSerializer):
    assigned_logical_devices_to_cid = LogicalInfoSerializer(many=True, read_only=True)
    inflicted_logical_devices = LogicalInfoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Computer
        fields = (
            'default_logical_device',
            'assigned_logical_devices_to_cid',
            'inflicted_logical_devices'
        )


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


class PermissionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name')


class GroupInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class UserProfileSerializer(UserDetailsSerializer):
    groups = GroupInfoSerializer(many=True, read_only=True)
    user_permissions = PermissionInfoSerializer(many=True, read_only=True)
    domains = DomainInfoSerializer(many=True, read_only=True, source='userprofile.domains')
    domain_preference = serializers.IntegerField(source='userprofile.domain_preference.id', allow_null=True)
    scope_preference = serializers.IntegerField(source='userprofile.scope_preference.id', allow_null=True)

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('userprofile', {})
        domain_preference = profile_data.get('domain_preference')
        scope_preference = profile_data.get('scope_preference')

        instance = super(UserProfileSerializer, self).update(instance, validated_data)

        # get and update user profile
        profile = instance.userprofile
        if domain_preference:
            pk = domain_preference.get('id', 0)
            if pk:
                domain = get_object_or_404(models.Domain, pk=pk)
                if domain.id in list(profile.domains.values_list('id', flat=True)):
                    profile.update_domain(domain)
            else:
                profile.update_domain(0)
        if scope_preference:
            pk = scope_preference.get('id', 0)
            if pk:
                scope = get_object_or_404(models.Scope, pk=pk)
                profile.update_scope(scope)
            else:
                profile.update_scope(0)

        return instance

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + (
            'domains', 'domain_preference', 'scope_preference',
            'groups', 'user_permissions',
        )
