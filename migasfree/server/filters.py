# -*- coding: utf-8 -*-

import django_filters

from django.contrib.admin.filters import ChoicesFieldListFilter
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django.utils.translation import ugettext as _
from rest_framework import filters

from .models import (
    ClientProperty, TagType, Computer,
    Store, Property, Version, Attribute,
    Package, Repository, Error, FaultDef,
    Fault, Notification, Migration,
    HwNode, Checking, Update, StatusLog,
)


class ProductiveFilterSpec(ChoicesFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super(ProductiveFilterSpec, self).__init__(
            field, request, params, model, model_admin, field_path
        )
        self.lookup_kwarg = '%s__in' % field_path
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


class TagFilter(SimpleListFilter):
    title = _('Tag Type')
    parameter_name = 'Tag'

    def lookups(self, request, model_admin):
        return [(c.id, c.name) for c in TagType.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(property_att__id__exact=self.value())
        else:
            return queryset


class FeatureFilter(SimpleListFilter):
    title = _('Property')
    parameter_name = 'Attribute'

    def lookups(self, request, model_admin):
        return [(c.id, c.name) for c in ClientProperty.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(property_att__id__exact=self.value())
        else:
            return queryset


class UserFaultFilter(SimpleListFilter):
    title = _('User')
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        return (
            ('me', _('To check for me')),
            ('only_me', _('Assigned to me')),
            ('others', _('Assigned to others')),
            ('no_assign', _('Not assigned')),
        )

    def queryset(self, request, queryset):
        lst = [request.user.id]
        if self.value() == 'me':
            return queryset.filter(
                Q(faultdef__users__id__in=lst) | Q(faultdef__users=None)
            )
        elif self.value() == 'only_me':
            return queryset.filter(Q(faultdef__users__id__in=lst))
        elif self.value() == 'others':
            return queryset.exclude(
                faultdef__users__id__in=lst
            ).exclude(faultdef__users=None)
        elif self.value() == 'no_assign':
            return queryset.filter(Q(faultdef__users=None))


class AttributeFilter(filters.FilterSet):
    class Meta:
        model = Attribute
        fields = ['id', 'property_att__id', 'property_att__prefix', 'value']


class CheckingFilter(filters.FilterSet):
    class Meta:
        model = Checking
        fields = ['id', 'active']


class ComputerFilter(filters.FilterSet):
    platform = django_filters.NumberFilter(name='version__platform__id')
    created_at = django_filters.DateFilter(name='created_at', lookup_type='gte')
    mac_address = django_filters.CharFilter(
        name='mac_address', lookup_type='icontains'
    )

    class Meta:
        model = Computer
        fields = [
            'id', 'version__id', 'status', 'name', 'uuid',
            'sync_attributes__id', 'tags__id'
        ]


class ErrorFilter(filters.FilterSet):
    date = django_filters.DateFilter(name='date', lookup_type='gte')
    date__lt = django_filters.DateFilter(name='date', lookup_expr='date__lt')
    platform = django_filters.NumberFilter(name='version__platform__id')

    class Meta:
        model = Error
        fields = ['id', 'version__id', 'checked', 'computer__id']


class FaultDefinitionFilter(filters.FilterSet):
    class Meta:
        model = FaultDef
        fields = ['id', 'attributes__id', 'active']


class FaultFilter(filters.FilterSet):
    date = django_filters.DateFilter(name='date', lookup_type='gte')
    date__lt = django_filters.DateFilter(name='date', lookup_expr='date__lt')

    class Meta:
        model = Fault
        fields = [
            'id', 'version__id', 'checked', 'faultdef__id', 'computer__id'
        ]


class MigrationFilter(filters.FilterSet):
    date = django_filters.DateFilter(name='date', lookup_type='gte')
    date__lt = django_filters.DateFilter(name='date', lookup_expr='date__lt')

    class Meta:
        model = Migration
        fields = ['id', 'version__id', 'computer__id']


class NodeFilter(filters.FilterSet):
    class Meta:
        model = HwNode
        fields = [
            'computer__id', 'id', 'parent', 'product', 'level',
            'width', 'name', 'classname', 'enabled', 'claimed',
            'description', 'vendor', 'serial', 'businfo', 'physid',
            'slot', 'size', 'capacity', 'clock', 'dev'
        ]


class NotificationFilter(filters.FilterSet):
    date = django_filters.DateFilter(name='date', lookup_type='gte')

    class Meta:
        model = Notification
        fields = ['id', 'checked']


class PackageFilter(filters.FilterSet):
    class Meta:
        model = Package
        fields = ['id', 'version__id', 'store__id']


class PropertyFilter(filters.FilterSet):
    class Meta:
        model = Property
        fields = ['id', 'active', 'tag']


class RepositoryFilter(filters.FilterSet):
    included_attributes = django_filters.CharFilter(
        name='attributes__value', lookup_type='icontains'
    )
    excluded_attributes = django_filters.CharFilter(
        name='excludes__value', lookup_type='icontains'
    )
    available_packages = django_filters.CharFilter(
        name='packages__name', lookup_type='icontains'
    )

    class Meta:
        model = Repository
        fields = ['id', 'version__id', 'active', 'schedule__id']


class StatusLogFilter(filters.FilterSet):
    created_at = django_filters.DateFilter(name='created_at', lookup_type='gte')
    created_at__lt = django_filters.DateFilter(name='created_at', lookup_expr='lt')

    class Meta:
        model = StatusLog
        fields = ['id', 'computer__id']


class StoreFilter(filters.FilterSet):
    class Meta:
        model = Store
        fields = ['id', 'version__id']


class UpdateFilter(filters.FilterSet):
    date = django_filters.DateFilter(name='date', lookup_type='gte')
    date__lt = django_filters.DateFilter(name='date', lookup_expr='date__lt')

    class Meta:
        model = Update
        fields = ['id', 'version__id', 'computer__id']


class VersionFilter(filters.FilterSet):
    class Meta:
        model = Version
        fields = ['id', 'platform__id', 'name']
