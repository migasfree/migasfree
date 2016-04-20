# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models
from django.core.urlresolvers import resolve
from django.utils.translation import ugettext_lazy as _

from .migasfree import MigasAdmin

from ..models import (
    DeviceType, DeviceFeature, DeviceManufacturer, DeviceConnection,
    DeviceDriver, DeviceLogical, DeviceModel, Device
)
from ..forms import DeviceLogicalForm, ExtraThinTextarea


@admin.register(DeviceType)
class DeviceTypeAdmin(MigasAdmin):
    list_display= ('name',)
    list_display_links = ('name',)
    ordering = ('name',)


@admin.register(DeviceFeature)
class DeviceFeatureAdmin(MigasAdmin):
    list_display= ('name',)
    list_display_links = ('name',)
    ordering = ('name',)


@admin.register(DeviceManufacturer)
class DeviceManufacturerAdmin(MigasAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    ordering = ('name',)


@admin.register(DeviceConnection)
class DeviceConnectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'fields')
    list_select_related = ('devicetype',)
    ordering = ('devicetype__name', 'name')
    fields = ('devicetype', 'name', 'fields')

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['devicetype'].widget.can_add_related = False

        return form


@admin.register(DeviceDriver)
class DeviceDriverAdmin(MigasAdmin):
    list_display = ('name', 'model', 'version', 'feature')
    list_display_links = ('name',)
    fields = ('name', 'model', 'version', 'feature', 'install')

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['model'].widget.can_add_related = False
        form.base_fields['version'].widget.can_add_related = False
        form.base_fields['feature'].widget.can_add_related = False

        return form


@admin.register(DeviceLogical)
class DeviceLogicalAdmin(MigasAdmin):
    form = DeviceLogicalForm
    fields = ('device', 'feature', 'name', 'computers')
    list_select_related = ('device', 'feature')
    list_display = ('my_link', 'device_link', 'feature')
    ordering = ('device__name', 'feature__name')
    search_fields = (
        'id',
        'device__name',
        'device__model__name',
        'device__model__manufacturer__name',
        'feature__name',
    )

    def my_link(self, object):
        return object.link()

    my_link.short_description = _('Device Logical')

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['device'].widget.can_add_related = False
        form.base_fields['feature'].widget.can_add_related = False

        return form


class DeviceLogicalInline(admin.TabularInline):
    model = DeviceLogical
    form = DeviceLogicalForm
    fields = ('feature', 'name', 'computers')
    extra = 0

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        args = resolve(request.path).args
        if db_field.name == 'feature' and len(args):
            device = Device.objects.get(pk=args[0])
            if device.model.pk:
                kwargs['queryset'] = DeviceFeature.objects.filter(
                    devicedriver__model__id=device.model.pk,
                    devicedriver__version=request.user.userprofile.version
                )

        return super(DeviceLogicalInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )


@admin.register(Device)
class DeviceAdmin(MigasAdmin):
    list_display = ('my_link', 'location', 'model_link', 'connection')
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

    def my_link(self, object):
        return object.link()

    my_link.short_description = _('Device')

    class Media:
        js = ('js/device_admin.js',)

    def save_related(self, request, form, formsets, change):
        super(type(self), self).save_related(request, form, formsets, change)

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
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['model'].widget.can_add_related = False
        form.base_fields['connection'].widget.can_add_related = False

        return form


class DeviceDriverInline(admin.TabularInline):
    model = DeviceDriver
    formfield_overrides = {models.TextField: {'widget': ExtraThinTextarea}}
    fields = ('version', 'feature', 'name', 'install')
    ordering = ('version', 'feature')
    extra = 1


@admin.register(DeviceModel)
class DeviceModelAdmin(MigasAdmin):
    list_display = ('name', 'manufacturer', 'devicetype')
    list_display_links = ('name',)
    list_filter = ('devicetype', 'manufacturer')
    ordering = ('devicetype__name', 'manufacturer__name', 'name')
    search_fields = (
        'name',
        'manufacturer__name',
        'connections__devicetype__name'
    )
    inlines = [DeviceDriverInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['manufacturer'].widget.can_add_related = False
        form.base_fields['devicetype'].widget.can_add_related = False
        form.base_fields['connections'].widget.can_add_related = False

        return form
