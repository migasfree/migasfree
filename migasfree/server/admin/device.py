# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models
from django.core.urlresolvers import resolve

from .migasfree import MigasAdmin, MigasFields

from ..models import (
    DeviceType, DeviceFeature, DeviceManufacturer, DeviceConnection,
    DeviceDriver, DeviceLogical, DeviceModel, Device
)
from ..forms import DeviceLogicalForm, ExtraThinTextarea


@admin.register(DeviceType)
class DeviceTypeAdmin(MigasAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    ordering = ('name',)
    search_fields = ('name',)


@admin.register(DeviceFeature)
class DeviceFeatureAdmin(MigasAdmin):
    list_display = ('name_link',)
    list_display_links = ('name_link',)
    ordering = ('name',)
    search_fields = ('name',)

    name_link = MigasFields.link(model=DeviceFeature, name='name')


@admin.register(DeviceManufacturer)
class DeviceManufacturerAdmin(MigasAdmin):
    list_display = ('name_link',)
    list_display_links = ('name_link',)
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

    def get_form(self, request, obj=None, **kwargs):
        form = super(DeviceConnectionAdmin, self).get_form(
            request,
            obj,
            **kwargs
        )
        form.base_fields['device_type'].widget.can_add_related = False

        return form


@admin.register(DeviceDriver)
class DeviceDriverAdmin(MigasAdmin):
    list_display = ('__str__', 'model', 'project', 'feature')
    list_display_links = ('__str__',)
    list_filter = ('project', 'model')
    fields = ('name', 'model', 'project', 'feature', 'packages_to_install')
    search_fields = ('name',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(DeviceDriverAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['model'].widget.can_add_related = False
        form.base_fields['project'].widget.can_add_related = False
        form.base_fields['feature'].widget.can_add_related = False

        return form


@admin.register(DeviceLogical)
class DeviceLogicalAdmin(MigasAdmin):
    form = DeviceLogicalForm
    fields = ('device', 'feature', 'alternative_feature_name', 'attributes')
    list_select_related = ('device', 'feature')
    list_display = ('alternative_feature_name_link', 'device_link', 'feature_link')
    list_filter = ('device__model', 'feature')
    ordering = ('device__name', 'feature__name')
    search_fields = (
        'id',
        'device__name',
        'device__model__name',
        'device__model__manufacturer__name',
        'feature__name',
    )

    alternative_feature_name_link = MigasFields.link(
        model=DeviceLogical, name='alternative_feature_name'
    )
    device_link = MigasFields.link(
        model=DeviceLogical, name='device', order="device__name"
    )
    feature_link = MigasFields.link(
        model=DeviceLogical, name='feature', order="feature__name"
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(DeviceLogicalAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['device'].widget.can_add_related = False
        form.base_fields['feature'].widget.can_add_related = False

        return form


class DeviceLogicalInline(admin.TabularInline):
    model = DeviceLogical
    form = DeviceLogicalForm
    fields = ('feature', 'alternative_feature_name', 'attributes')
    extra = 0

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
    list_display = ('name_link', 'location', 'model_link', 'connection')
    list_filter = ('model',)
    search_fields = (
        'name',
        'model__name',
        'model__manufacturer__name',
        'data'
    )
    fields = ('name', 'model', 'connection', 'data')
    ordering = ('name',)
    inlines = [DeviceLogicalInline]

    name_link = MigasFields.link(model=Device, name='name')
    model_link = MigasFields.link(
        model=Device, name='model', order="model__name"
    )

    class Media:
        js = ('js/device_admin.js',)

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

    def get_form(self, request, obj=None, **kwargs):
        form = super(DeviceAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['model'].widget.can_add_related = False
        form.base_fields['connection'].widget.can_add_related = False

        return form

    def get_queryset(self, request):
        return super(DeviceAdmin, self).get_queryset(
            request
        ).select_related(
            'connection', 'connection__device_type',
            'model', 'model__manufacturer', 'model__device_type',
        ).prefetch_related(
            "devicelogical_set"
        )


class DeviceDriverInline(admin.TabularInline):
    model = DeviceDriver
    formfield_overrides = {models.TextField: {'widget': ExtraThinTextarea}}
    fields = ('project', 'feature', 'name', 'packages_to_install')
    ordering = ('project', 'feature')
    extra = 1


@admin.register(DeviceModel)
class DeviceModelAdmin(MigasAdmin):
    list_display = ('name_link', 'manufacturer_link', 'device_type')
    list_display_links = ('name_link',)
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
        model=DeviceModel, name='manufacturer', order="manufacturer__name"
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(DeviceModelAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['manufacturer'].widget.can_add_related = False
        form.base_fields['device_type'].widget.can_add_related = False
        form.base_fields['connections'].widget.can_add_related = False

        return form
