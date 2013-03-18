# -*- coding: utf-8 -*-

"""
Admin Models
"""

from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.shortcuts import redirect
from django import forms
from django.db import models
from django.core.urlresolvers import reverse

from migasfree.server.functions import trans
from migasfree.server.models import *
from migasfree.settings import (
    STATIC_URL,
    MIGASFREE_COMPUTER_SEARCH_FIELDS
)

#AJAX_SELECT
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin

#WIDGETS
from migasfree.server.widgets import MigasfreeSplitDateTime

migasfree_widgets = {
    models.DateTimeField: {'widget': MigasfreeSplitDateTime},
}

admin.site.register(DeviceType)
admin.site.register(DeviceManufacturer)
admin.site.register(DeviceConnection)
admin.site.register(UserProfile)
admin.site.register(AutoCheckError)
admin.site.register(Platform)


def user_version(user):
    """
    Returns the user's current version
    """
    try:
        version = UserProfile.objects.get(id=user.id).version.id
    except:
        version = None

    return version


class WideTextarea(forms.Textarea):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', {})
        attrs.setdefault('cols', 160)
        attrs.setdefault('rows', 5)
        super(WideTextarea, self).__init__(*args, **kwargs)


class VersionAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = ('name', 'platform', 'pms', 'computerbase', 'autoregister')
    actions = None

admin.site.register(Version, VersionAdmin)


class MigrationAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = ('id', 'computer_link', 'version_link', 'date')
    list_filter = ('date', 'version__platform', )
    search_fields = ('computer__name', 'date',)
    actions = None

admin.site.register(Migration, MigrationAdmin)


class UpdateAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = ('id', 'computer_link', 'user', 'date', 'version')
    list_filter = ('date', )
    search_fields = ('computer__name', 'date', 'user__name')
    actions = None

admin.site.register(Update, UpdateAdmin)


class CheckingAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = ('name', 'active', 'alert')
    list_filter = ('active', )

admin.site.register(Checking, CheckingAdmin)


class DeviceFileAdmin(admin.ModelAdmin):
#    list_display=('name', )
    pass

admin.site.register(DeviceFile, DeviceFileAdmin)


class ComputerInline(admin.TabularInline):
    model = Computer.devices.through


class DeviceAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = (
        'name',
        'alias',
        'device_connection_type',
        'device_manufacturer_name',
        'model',
        'device_connection_name'
    )
    list_filter = ('model',)
    search_fields = (
        'name',
        'alias',
        'model__name',
        'model__manufacturer__name'
    )
    fields = (
        'name',
        'alias',
        'model',
        'connection',
        'uri',
        'location',
        'information'
    )
    formfield_overrides = {models.TextField: {'widget': WideTextarea}}
    inlines = [ComputerInline, ]

admin.site.register(Device, DeviceAdmin)


class DeviceModelAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = ('name', 'manufacturer', 'devicetype')
    list_filter = ('devicetype', 'manufacturer')
    search_fields = (
        'name',
        'manufacturer__name',
        'connections__devicetype__name'
    )

admin.site.register(DeviceModel, DeviceModelAdmin)


class PmsAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = ('name',)

admin.site.register(Pms, PmsAdmin)


class StoreAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = ('name',)
    search_fields = ('name',)
    actions = ['information', 'download']

    def download(self, request, queryset):
        return redirect(
            STATIC_URL + '%s/STORES/%s/' % (
                queryset[0].version.name,
                queryset[0].name
            )
        )

    download.short_description = trans("Download")

    def information(self, request, queryset):
        return redirect(
            reverse(
                'package_info',
                args=('STORES/%s/' % queryset[0].name,)
            )
        )

    information.short_description = trans("Information of Package")

admin.site.register(Store, StoreAdmin)


class PropertyAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = ('prefix', 'name', 'active', 'kind', 'auto',)
    list_filter = ('active',)
    ordering = ('name',)
    search_fields = ('user__name', 'user__fullname', 'computer__name')

admin.site.register(Property, PropertyAdmin)


class AttributeAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = ('value', 'description', 'property_link',)
    list_filter = ('property_att',)
    ordering = ('property_att', 'value',)
    search_fields = ('value', 'description')

admin.site.register(Attribute, AttributeAdmin)


class LoginAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    form = make_ajax_form(Login, {'attributes': 'attribute'})

    list_display = ('id', 'user_link', 'computer_link', 'date',)
    list_filter = ('date',)
    ordering = ('user', 'computer',)
    search_fields = ['user__name', 'user__fullname']
    for field in MIGASFREE_COMPUTER_SEARCH_FIELDS:
        search_fields.append("computer__%s" % field)

    search_fields = tuple(search_fields)

    fieldsets = (
        (None, {
            'fields': ('date', 'user', 'computer',)
        }),
        ('Atributtes', {
            'classes': ('collapse',),
            'fields': ('attributes',)
        }),
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "attributes":
            kwargs["queryset"] = Attribute.objects.filter(
                property_att__active=True
            )
            #kwargs['widget'] = FilteredSelectMultiple(
            #    db_field.verbose_name,
            #    (db_field.name in self.filter_vertical)
            #)
            return db_field.formfield(**kwargs)

        return super(LoginAdmin, self).formfield_for_manytomany(
            db_field,
            request,
            **kwargs
        )

admin.site.register(Login, LoginAdmin)


class UserAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = ('name', 'fullname',)
    ordering = ('name',)
    search_fields = ('name', 'fullname')

admin.site.register(User, UserAdmin)


class NotificationAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = (
        'id',
        'checked',
        'date',
        'notification',
    )
    list_filter = ('checked', 'date')
    ordering = ('date',)
    search_fields = ('date', 'notification',)

    actions = ['checked_ok']

    def checked_ok(self, request, queryset):
        for noti in queryset:
            noti.checked = True
            noti.save()

        return redirect("%s?checked__exact=0"
            % reverse('admin:server_notification_changelist'))

    checked_ok.short_description = trans("Checking is O.K.")

admin.site.register(Notification, NotificationAdmin)


class ErrorAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = (
        'id',
        'computer_link',
        'version',
        'checked',
        'date',
        'error',
    )
    list_filter = ('checked', 'date', "version")
    ordering = ('date', 'computer',)
    search_fields = ('date', 'computer__name', 'error',)

    actions = ['checked_ok']

    def checked_ok(self, request, queryset):
        for error in queryset:
            error.checked = True
            error.save()

        return redirect("%s?checked__exact=0"
            % reverse('admin:server_error_changelist'))

    checked_ok.short_description = trans("Checking is O.K.")

admin.site.register(Error, ErrorAdmin)


class FaultAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = (
        'id',
        'computer_link',
        'version',
        'checked',
        'date',
        'text',
        'faultdef',
    )
    list_filter = ('checked', 'date', 'version', 'faultdef',)
    ordering = ('date', 'computer',)
    search_fields = ('date', 'computer__name', 'faultdef__name')

    actions = ['checked_ok']

    def checked_ok(self, request, queryset):
        for fault in queryset:
            fault.checked = True
            fault.save()

        return redirect("%s?checked__exact=0"
            % reverse('admin:server_fault_changelist'))

    checked_ok.short_description = trans("Checking is O.K.")

admin.site.register(Fault, FaultAdmin)


class FaultDefAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    form = make_ajax_form(FaultDef, {'attributes': 'attribute'})
    list_display = ('name', 'active', 'list_attributes',)
    list_filter = ('active',)
    ordering = ('name',)
    search_fields = ('name', 'function',)
    filter_horizontal = ('attributes',)

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'active', 'language', 'code')
        }),
        ('Atributtes', {
            'classes': ('collapse',),
            'fields': ('attributes',)
        }),
    )

admin.site.register(FaultDef, FaultDefAdmin)


class ComputerAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    form = make_ajax_form(Computer, {
        'tags': 'tag',
    })

    list_display = (
        'link',
        'version',
        'ip',
        'login_link',
        'datelastupdate',
        'hw_link',

    )
    ordering = ('name',)
    list_filter = ('version',)
    search_fields = MIGASFREE_COMPUTER_SEARCH_FIELDS

    def formfield_for_manytomany(self, db_field, request, **kwargs):

        if db_field.name == "devices":
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name,
                (db_field.name in self.filter_vertical)
            )
            return db_field.formfield(**kwargs)

        return super(ComputerAdmin, self).formfield_for_manytomany(
            db_field,
            request,
            **kwargs
        )

admin.site.register(Computer, ComputerAdmin)


class MessageAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    formfield_overrides = migasfree_widgets
    list_display = ('id', 'computer_link', 'date', 'text',)
    ordering = ('date',)
    list_filter = ('date',)
    search_fields = ('computer', 'text', 'date',)

admin.site.register(Message, MessageAdmin)


class MessageServerAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'text',)
    ordering = ('date',)
    list_filter = ('date',)
    search_fields = ('text', 'date',)

admin.site.register(MessageServer, MessageServerAdmin)


class RepositoryAdmin(AjaxSelectAdmin):
    formfield_overrides = migasfree_widgets
    form = make_ajax_form(Repository, {
        'attributes': 'attribute',
        'packages': 'package',
        'excludes': 'attribute'
    })

    list_display = ('name', 'active', 'date', 'schedule', 'timeline',)
    list_filter = ('active',)
    ordering = ('name',)
    search_fields = ('name', 'packages__name',)
    #filter_horizontal = ('attributes', 'packages',)
    actions = None

    fieldsets = (
        ('General', {
            'fields': ('name', 'version', 'active', 'comment', )
        }),
        ('Schedule', {
            'fields': ('date', 'schedule',)
        }),
        ('Packages', {
            'classes': ('collapse',),
            'fields': ('packages', 'toinstall', 'toremove',)
        }),
        ('Atributtes', {
            'classes': ('collapse',),
            'fields': ('attributes', 'excludes')
        }),
    )

    # QuerySet filter by user version.
    def queryset(self, request):
        if request.user.is_superuser:
            return self.model._default_manager.get_query_set()
        else:
            return self.model._default_manager.get_query_set().filter(
                version=user_version(request.user)
            )

    # Packages filter by user version
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "packages":
            kwargs["queryset"] = Package.objects.filter(
                version=user_version(request.user)
            )
            #kwargs['widget'] = FilteredSelectMultiple(
            #    db_field.verbose_name,
            #    (db_field.name in self.filter_vertical)
            #)

            return db_field.formfield(**kwargs)

        if db_field.name == "attributes":
            kwargs["queryset"] = Attribute.objects.filter(
                property_att__active=True
            )
            #kwargs['widget'] = FilteredSelectMultiple(
            #    db_field.verbose_name,
            #    (db_field.name in self.filter_vertical)
            #)

            return db_field.formfield(**kwargs)

        return super(RepositoryAdmin, self).formfield_for_manytomany(
            db_field,
            request,
            **kwargs
        )

admin.site.register(Repository, RepositoryAdmin)


class ScheduleDelayline(admin.TabularInline):
    formfield_overrides = migasfree_widgets
    model = ScheduleDelay
    form = make_ajax_form(ScheduleDelay, {'attributes': 'attribute'})
    extra = 0
    ordering = ('delay',)


class ScheduleAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = ('name', 'description',)
    inlines = [ScheduleDelayline, ]
    extra = 0

admin.site.register(Schedule, ScheduleAdmin)


class PackageAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = ('name', 'store',)
    list_filter = ('store',)
    search_fields = ('name', 'store__name',)
    ordering = ('name',)

    actions = ['information', 'download']

    def information(self, request, queryset):
        return redirect(
            reverse(
                'package_info',
                args=('STORES/%s/%s' % (
                    queryset[0].store.name,
                    queryset[0].name
                ),)
            )
        )

    information.short_description = trans("Information of Package")

    def download(self, request, queryset):
        return redirect(STATIC_URL + '%s/STORES/%s/%s' % (
            queryset[0].version.name,
            queryset[0].store.name,
            queryset[0].name
        ))

    download.short_description = trans("Download")

admin.site.register(Package, PackageAdmin)


class QueryAdmin(admin.ModelAdmin):
    formfield_overrides = migasfree_widgets
    list_display = ('name', 'description',)
    actions = ['run_query']

    def run_query(self, request, queryset):
        for query in queryset:
            return redirect(reverse('query', args=(query.id, )))

    run_query.short_description = trans("Run Query")

admin.site.register(Query, QueryAdmin)
