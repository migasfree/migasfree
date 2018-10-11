# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models
from django.urls import resolve
from django.utils.translation import ugettext_lazy as _

from .migasfree import MigasAdmin, MigasFields

from ..models import (
    DeviceType, DeviceFeature, DeviceManufacturer, DeviceConnection,
    DeviceDriver, DeviceLogical, DeviceModel, Device
)
from ..forms import (
    DeviceLogicalForm, DeviceModelForm,
    DeviceForm, ExtraThinTextarea,
)

from ..filters import (
    ModelFilter
)


@admin.register(DeviceType)
class DeviceTypeAdmin(MigasAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    ordering = ('name',)
    search_fields = ('name',)


@admin.register(DeviceFeature)
class DeviceFeatureAdmin(MigasAdmin):
    list_display = ('name_link',)
    ordering = ('name',)
    search_fields = ('name',)

    name_link = MigasFields.link(model=DeviceFeature, name='name')


@admin.register(DeviceManufacturer)
class DeviceManufacturerAdmin(MigasAdmin):
    list_display = ('name_link',)
    ordering = ('name',)
    search_fields = ('name',)

    name_link = MigasFields.link(model=DeviceManufacturer, name='name')


@admin.register(DeviceConnection)
class DeviceConnectionAdmin(MigasAdmin):
    list_display = ('name_link', 'device_type', 'fields')
    list_select_related = ('device_type',)
    ordering = ('device_type__name', 'name')
    fields = ('device_type', 'name', 'fields')
    search_fields = ('name',)

    name_link = MigasFields.link(model=DeviceConnection, name='name')


@admin.register(DeviceDriver)
class DeviceDriverAdmin(MigasAdmin):
    list_display = ('__str__', 'model', 'project', 'feature')
    list_display_links = ('__str__',)
    list_filter = ('project', 'model')
    fields = ('name', 'model', 'project', 'feature', 'packages_to_install')
    search_fields = ('name',)


@admin.register(DeviceLogical)
class DeviceLogicalAdmin(MigasAdmin):
    form = DeviceLogicalForm
    fields = ('device', 'feature', 'alternative_feature_name', 'attributes')
    list_select_related = ('device', 'feature')
    list_display = ('device_logical_link', 'alternative_feature_name', 'device_link', 'feature_link')
    list_filter = ('device__model', 'feature')
    ordering = ('device__name', 'feature__name')
    search_fields = (
        'id',
        'device__name',
        'device__model__name',
        'device__model__manufacturer__name',
        'feature__name',
    )

    def device_logical_link(self, obj):
        return obj.link()

    device_logical_link.short_description = _('Device Logical')
    device_logical_link.admin_order_field = 'id'

    device_link = MigasFields.link(
        model=DeviceLogical, name='device', order='device__name'
    )
    feature_link = MigasFields.link(
        model=DeviceLogical, name='feature', order='feature__name'
    )


class DeviceLogicalInline(admin.TabularInline):
    model = DeviceLogical
    form = DeviceLogicalForm
    fields = ('feature', 'alternative_feature_name', 'attributes')
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(DeviceLogicalInline, self).get_formset(request, obj, **kwargs)
        formset.form.base_fields['feature'].widget.can_change_related = False
        formset.form.base_fields['feature'].widget.can_add_related = False

        return formset

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        args = resolve(request.path).args
        if db_field.name == 'feature' and len(args):
            device = Device.objects.get(pk=args[0])
            if device.model.pk:
                kwargs['queryset'] = DeviceFeature.objects.filter(
                    devicedriver__model__id=device.model.pk
                ).distinct()

        return super(DeviceLogicalInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )


@admin.register(Device)
class DeviceAdmin(MigasAdmin):
    form = DeviceForm
    list_display = ('name_link', 'location', 'model_link', 'connection_link', 'computers')
    list_filter = (ModelFilter, 'connection', 'model__manufacturer')
    search_fields = (
        'name',
        'model__name',
        'model__manufacturer__name',
        'data'
    )
    fields = ('name', 'model', 'connection', 'available_for_attributes', 'data')
    ordering = ('name',)
    inlines = [DeviceLogicalInline]

    name_link = MigasFields.link(model=Device, name='name')
    model_link = MigasFields.link(
        model=Device, name='model', order='model__name'
    )
    connection_link = MigasFields.link(
        model=Device, name='connection', order='connection__name'
    )

    def computers(self, obj):
        related_objects = obj.related_objects('computer', self.user.userprofile)
        if related_objects:
            return related_objects.count()

        return 0

    computers.short_description = _('Computers')

    def save_related(self, request, form, formsets, change):
        super(DeviceAdmin, self).save_related(request, form, formsets, change)

        device = form.instance
        for feature in DeviceFeature.objects.filter(
            devicedriver__model__id=device.model.id
        ).distinct():
            if DeviceLogical.objects.filter(
                device__id=device.id,
                feature=feature
            ).count() == 0:
                device.devicelogical_set.create(
                    device=device,
                    feature=feature
                )

    def get_queryset(self, request):
        self.user = request.user
        return super(DeviceAdmin, self).get_queryset(
            request
        ).select_related(
            'connection', 'connection__device_type',
            'model', 'model__manufacturer', 'model__device_type',
        ).prefetch_related(
            'devicelogical_set'
        )

    class Media:
        js = ('js/device_admin.js',)


class DeviceDriverInline(admin.TabularInline):
    model = DeviceDriver
    formfield_overrides = {models.TextField: {'widget': ExtraThinTextarea}}
    fields = ('project', 'feature', 'name', 'packages_to_install')
    ordering = ('project', 'feature')
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(DeviceDriverInline, self).get_formset(request, obj, **kwargs)
        formset.form.base_fields['project'].widget.can_change_related = False
        formset.form.base_fields['project'].widget.can_add_related = False
        formset.form.base_fields['feature'].widget.can_change_related = False
        formset.form.base_fields['feature'].widget.can_add_related = False

        return formset


@admin.register(DeviceModel)
class DeviceModelAdmin(MigasAdmin):
    form = DeviceModelForm
    list_display = ('name_link', 'manufacturer_link', 'device_type')
    list_filter = ('device_type', 'manufacturer')
    ordering = ('device_type__name', 'manufacturer__name', 'name')
    search_fields = (
        'name',
        'manufacturer__name',
        'connections__device_type__name'
    )
    inlines = [DeviceDriverInline]

    name_link = MigasFields.link(model=DeviceModel, name='name')
    manufacturer_link = MigasFields.link(
        model=DeviceModel, name='manufacturer', order='manufacturer__name'
    )
