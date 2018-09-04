# -*- coding: utf-8 -*-

import django_filters

from datetime import datetime, timedelta

from django.db.models import Q
from django.contrib.admin import SimpleListFilter, RelatedFieldListFilter, ListFilter
from django.contrib.admin.filters import ChoicesFieldListFilter
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _

from .models import (
    ServerProperty, Computer,
    Store, Property, Project, Attribute, AttributeSet,
    Package, Deployment, Error, FaultDefinition,
    Fault, Notification, Migration,
    HwNode, Synchronization, StatusLog,
    Device, DeviceDriver, ScheduleDelay, Platform,
)


class ProductiveFilterSpec(ChoicesFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super(ProductiveFilterSpec, self).__init__(
            field, request, params, model, model_admin, field_path
        )

        self.user = request.user.userprofile
        self.lookup_kwarg = '{}__in'.format(field_path)
        self.lookup_val = request.GET.get(self.lookup_kwarg)
        self.title = _('Status')

    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
            'display': _('All')
        }

        status = [
            ('intended,reserved,unknown,available,in repair', _("Subscribed")),
            ('intended,reserved,unknown', "* " + _("Productive")),
            ('intended', "--- " + _("intended")),
            ('reserved', "--- " + _("reserved")),
            ('unknown', "--- " + _("unknown")),
            ('available,in repair', "* " + _("Unproductive")),
            ('in repair', "--- " + _("in repair")),
            ('available', "--- " + _("available")),
            ('unsubscribed', _('unsubscribed'))
        ]
        for item in status:
            yield {
                'selected': self.lookup_val == item[0],
                'query_string': cl.get_query_string(
                    {self.lookup_kwarg: item[0]}
                ),
                'display': item[1]
            }


class ServerAttributeFilter(SimpleListFilter):
    title = _('Tag Category')
    parameter_name = 'Tag'

    def lookups(self, request, model_admin):
        if request.user.userprofile.is_view_all():
            return [(c.id, c.name) for c in ServerProperty.objects.all()]
        else:
            return [(c.id, c.name) for c in ServerProperty.objects.filter(
                Q(attribute__in=request.user.userprofile.get_attributes()) |
                Q(attribute__in=request.user.userprofile.get_domain_tags())
            ).distinct()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(property_att__id__exact=self.value())
        else:
            return queryset


class ClientAttributeFilter(SimpleListFilter):
    title = _('Property')
    parameter_name = 'Attribute'

    def lookups(self, request, model_admin):
        return [
            (c.id, c.name) for c in Property.objects.filter(
                Q(sort='client') | Q(sort='basic')
            )
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(property_att__id__exact=self.value())
        else:
            return queryset


class UserFaultFilter(SimpleListFilter):
    title = _('User')
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        return Fault.USER_FILTER_CHOICES

    def queryset(self, request, queryset):
        lst = [request.user.id]
        if self.value() == 'me':
            return queryset.filter(
                Q(fault_definition__users__id__in=lst) |
                Q(fault_definition__users=None)
            )
        elif self.value() == 'only_me':
            return queryset.filter(fault_definition__users__id__in=lst)
        elif self.value() == 'others':
            return queryset.exclude(
                fault_definition__users__id__in=lst
            ).exclude(fault_definition__users=None)
        elif self.value() == 'unassigned':
            return queryset.filter(fault_definition__users=None)


class SoftwareInventoryFilter(SimpleListFilter):
    title = _('Software Inventory')
    parameter_name = 'software_inventory'

    def lookups(self, request, model_admin):
        return [
            ('without', _('Without software inventory'))
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                Q(software_inventory__isnull=True)
                | Q(software_inventory__startswith='-')
                | Q(software_inventory='-')
            )
        else:
            return queryset


class SyncEndDateFilter(SimpleListFilter):
    title = _('Synchronization End Date')
    parameter_name = 'sync_end_date_ago'

    def lookups(self, request, model_admin):
        return [
            (0, _('without date')),
            (7, _('%d days ago') % 7),
            (30, _('%d days ago') % 30),
            (60, _('%d days ago') % 60),
            (120, _('%d days ago') % 120),
            (180, _('%d days ago') % 180),
            (365, _('%d days ago') % 365),
        ]

    def queryset(self, request, queryset):
        if self.value() == 0:
            return queryset.filter(
                sync_end_date__isnull=True
            )
        if self.value() and int(self.value()) > 0:
            return queryset.filter(
                sync_end_date__lt=datetime.date(
                    datetime.now() - timedelta(days=int(self.value()))
                )
            )

        return queryset


class ProjectFilterAdmin(RelatedFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super(ProjectFilterAdmin, self).__init__(
            field, request, params, model, model_admin, field_path
        )
        if request.user.userprofile.is_view_all():
            qs = Project.objects.all()
        else:
            qs = Project.objects.scope(request.user.userprofile)

        self.lookup_choices = tuple((project.id, project.name) for project in qs)
        self.lookup_title = field.verbose_name
        self.title = self.lookup_title


class PlatformFilterAdmin(RelatedFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super(PlatformFilterAdmin, self).__init__(
            field, request, params, model, model_admin, field_path
        )
        if request.user.userprofile.is_view_all():
            qs = Platform.objects.all()
        else:
            qs = Platform.objects.filter(project__in=request.user.userprofile.get_projects()).distinct()

        self.lookup_choices = tuple((platform.id, platform.name) for platform in qs)
        self.lookup_title = field.verbose_name
        self.title = self.lookup_title


class AttributeSetFilter(django_filters.FilterSet):
    class Meta:
        model = AttributeSet
        fields = ['id', 'enabled']


class AttributeFilter(django_filters.FilterSet):
    class Meta:
        model = Attribute
        fields = ['id', 'property_att__id', 'property_att__prefix', 'value', 'property_att__sort']


class ComputerFilter(django_filters.FilterSet):
    platform = django_filters.NumberFilter(field_name='project__platform__id')
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    mac_address = django_filters.CharFilter(
        field_name='mac_address', lookup_expr='icontains'
    )

    class Meta:
        model = Computer
        fields = [
            'id', 'project__id', 'status', 'name', 'uuid',
            'sync_attributes__id', 'tags__id'
        ]


class ErrorFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lt = django_filters.DateFilter(field_name='created_at', lookup_expr='lt')
    platform = django_filters.NumberFilter(field_name='project__platform__id')

    class Meta:
        model = Error
        fields = ['id', 'project__id', 'checked', 'computer__id']


class FaultDefinitionFilter(django_filters.FilterSet):
    class Meta:
        model = FaultDefinition
        fields = [
            'id', 'enabled',
            'included_attributes__id', 'excluded_attributes'
        ]


class FaultFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lt = django_filters.DateFilter(field_name='created_at', lookup_expr='lt')

    class Meta:
        model = Fault
        fields = [
            'id', 'project__id', 'checked', 'fault_definition__id', 'computer__id'
        ]


class MigrationFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lt = django_filters.DateFilter(field_name='created_at', lookup_expr='lt')

    class Meta:
        model = Migration
        fields = ['id', 'project__id', 'computer__id']


class NodeFilter(django_filters.FilterSet):
    class Meta:
        model = HwNode
        fields = [
            'computer__id', 'id', 'parent', 'product', 'level',
            'width', 'name', 'class_name', 'enabled', 'claimed',
            'description', 'vendor', 'serial', 'bus_info', 'physid',
            'slot', 'size', 'capacity', 'clock', 'dev'
        ]


class NotificationFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')

    class Meta:
        model = Notification
        fields = ['id', 'checked']


class PackageFilter(django_filters.FilterSet):
    class Meta:
        model = Package
        fields = ['id', 'project__id', 'store__id']


class PropertyFilter(django_filters.FilterSet):
    class Meta:
        model = Property
        fields = ['id', 'enabled', 'sort']


class DeploymentFilter(django_filters.FilterSet):
    included_attributes = django_filters.CharFilter(
        field_name='included_attributes__value', lookup_expr='icontains'
    )
    excluded_attributes = django_filters.CharFilter(
        field_name='excluded_attributes__value', lookup_expr='icontains'
    )
    available_packages = django_filters.CharFilter(
        field_name='available_packages__name', lookup_expr='icontains'
    )

    class Meta:
        model = Deployment
        fields = ['id', 'project__id', 'enabled', 'schedule__id']


class StatusLogFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lt = django_filters.DateFilter(field_name='created_at', lookup_expr='lt')

    class Meta:
        model = StatusLog
        fields = ['id', 'computer__id']


class StoreFilter(django_filters.FilterSet):
    class Meta:
        model = Store
        fields = ['id', 'project__id']


class SynchronizationFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lt = django_filters.DateFilter(field_name='created_at', lookup_expr='lt')

    class Meta:
        model = Synchronization
        fields = ['id', 'project__id', 'computer__id']


class ProjectFilter(django_filters.FilterSet):
    class Meta:
        model = Project
        fields = ['id', 'platform__id', 'name']


class DeviceFilter(django_filters.FilterSet):
    class Meta:
        model = Device
        fields = ['model__id', 'model__name']


class DriverFilter(django_filters.FilterSet):
    class Meta:
        model = DeviceDriver
        fields = [
            'project__id', 'project__name',
            'model__id', 'model__name',
            'feature__id', 'feature__name'
        ]


class ScheduleDelayFilter(django_filters.FilterSet):
    class Meta:
        model = ScheduleDelay
        fields = ['schedule__id', 'schedule__name']


class SingleTextInputFilter(ListFilter):
    """
    renders filter form with text input and submit button
    """
    parameter_name = None
    template = "admin/singletext_input_filter.html"

    def __init__(self, request, params, model, model_admin):
        super(SingleTextInputFilter, self).__init__(
            request, params, model, model_admin)
        if self.parameter_name is None:
            raise ImproperlyConfigured(
                "The list filter '%s' does not specify "
                "a 'parameter_name'." % self.__class__.__name__)

        if self.parameter_name in params:
            value = params.pop(self.parameter_name)
            self.used_parameters[self.parameter_name] = value

    def value(self):
        """
        Returns the value (in string format) provided in the request's
        query string for this filter, if any. If the value wasn't provided then
        returns None.
        """
        return self.used_parameters.get(self.parameter_name, None)

    def has_output(self):
        return True

    def expected_parameters(self):
        """
        Returns the list of parameter names that are expected from the
        request's query string and that will be used by this filter.
        """
        return [self.parameter_name]

    def choices(self, cl):
        all_choice = {
            'selected': self.value() is None,
            'query_string': cl.get_query_string({}, [self.parameter_name]),
            'display': _('All'),
        }
        return ({
            'get_query': cl.params,
            'current_value': self.value(),
            'all_choice': all_choice,
            'parameter_name': self.parameter_name
        }, )


class DomainFilter(SingleTextInputFilter):
    title = 'domain editable'
    parameter_name = 'domain'

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(domain__name__icontains=self.value())


class ModelFilter(SingleTextInputFilter):
    title = 'model'
    parameter_name = 'model'

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(model__name__icontains=self.value())
