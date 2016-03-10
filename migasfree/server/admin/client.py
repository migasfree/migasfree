# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib import admin, messages
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin

from .migasfree import MigasAdmin

from ..filters import ProductiveFilterSpec, UserFaultFilter
from ..forms import ComputerForm
from ..resources import ComputerResource
from ..models import (
    AutoCheckError, Computer, Error, Fault, FaultDef, Login, Message,
    Migration, Notification, StatusLog, Update, User
)

admin.site.register(AutoCheckError)


def add_computer_search_fields(fields_list):
    for field in settings.MIGASFREE_COMPUTER_SEARCH_FIELDS:
        fields_list.append("computer__%s" % field)

    return tuple(fields_list)


@admin.register(Computer)
class ComputerAdmin(AjaxSelectAdmin, MigasAdmin):
    form = ComputerForm
    list_display = (
        'my_link',
        'version',
        'status',
        'ip',
        'login_link',
        'datelastupdate',
        'hw_link',
    )
    list_per_page = 25
    ordering = ('name',)
    list_filter = ('version', ('status', ProductiveFilterSpec))
    search_fields = settings.MIGASFREE_COMPUTER_SEARCH_FIELDS
    list_select_related = False

    readonly_fields = (
        'name',
        'uuid',
        'version',
        'dateinput',
        'datelastupdate',
        'ip',
        'software',
        'history_sw',
        'hw_link',
        'machine',
        'cpu',
        'ram',
        'storage',
        'disks',
        'mac_address',
    )

    fieldsets = (
        (_('General'), {
            'fields': (
                'status',
                'name',
                'version',
                'dateinput',
                'datelastupdate',
                'ip',
            )
        }),
        (_('Hardware'), {
            'fields': (
                'datehardware',
                'hw_link',
                'uuid',
                'machine',
                'cpu',
                'ram',
                'storage',
                'disks',
                'mac_address',
            )
        }),
        (_('Software'), {
            'classes': ('collapse',),
            'fields': ('software', 'history_sw',)
        }),
        (_('Devices'), {
            'fields': ('devices_logical', )
        }),
        (_('Tags'), {
            'fields': ('tags', )
        }),
    )

    resource_class = ComputerResource
    actions = ['delete_selected', 'reinstall_devices']

    def my_link(self, object):
        return object.link()

    my_link.short_description = _('Computer')

    def delete_selected(self, request, objects):
        if not self.has_delete_permission(request):
            raise PermissionDenied

        return render(
            request,
            'computer_confirm_delete_selected.html',
            {
                'object_list': ', '.join([x.__str__() for x in objects])
            }
        )

    delete_selected.short_description = _("Delete selected "
        "%(verbose_name_plural)s")

    def reinstall_devices(self, request, objects):
        for item in objects:
            item.remove_device_copy()

        messages.success(request, _('Ready computers to reinstall devices'))

        return redirect(request.get_full_path())

    reinstall_devices.short_description = _("Reinstall devices")

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "devices_logical":
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name,
                (db_field.name in self.filter_vertical)
            )
            return db_field.formfield(**kwargs)

        return super(type(self), self).formfield_for_manytomany(
            db_field,
            request,
            **kwargs
        )

    def has_add_permission(self, request):
        return False


@admin.register(Error)
class ErrorAdmin(MigasAdmin):
    list_display = (
        'id',
        'computer_link',
        'version',
        'my_checked',
        'date',
        'truncated_error',
    )
    list_display_links = ('id',)
    list_filter = ('checked', 'date', 'version__platform', 'version')
    #list_editable = ('checked',)  # TODO
    ordering = ('-date', 'computer',)
    search_fields = add_computer_search_fields(['date', 'error'])
    readonly_fields = ('computer_link', 'version', 'date', 'error')
    exclude = ('computer',)

    def my_checked(self, obj):
        return self.boolean_field(obj.checked)

    my_checked.allow_tags = True
    my_checked.short_description = _('checked')

    actions = ['checked_ok']

    def checked_ok(self, request, queryset):
        for item in queryset:
            item.okay()

        messages.success(request, _('Checked %s') % _('Errors'))

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

    def has_add_permission(self, request):
        return False


@admin.register(Fault)
class FaultAdmin(MigasAdmin):
    list_display = (
        'id',
        'computer_link',
        'version',
        'my_checked',
        'date',
        'text',
        'faultdef',
        #'list_users'  # performance improvement
    )
    list_display_links = ('id',)
    list_filter = (
        UserFaultFilter, 'checked', 'date',
        'version__platform', 'version', 'faultdef'
    )
    ordering = ('-date', 'computer',)
    search_fields = add_computer_search_fields(['date', 'faultdef__name'])
    readonly_fields = ('computer_link', 'faultdef', 'version', 'date', 'text')
    exclude = ('computer',)

    def my_checked(self, obj):
        return self.boolean_field(obj.checked)

    my_checked.allow_tags = True
    my_checked.short_description = _('checked')

    actions = ['checked_ok']

    def checked_ok(self, request, queryset):
        for item in queryset:
            item.okay()

        messages.success(request, _('Checked %s') % _('Faults'))

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

    def has_add_permission(self, request):
        return False


@admin.register(FaultDef)
class FaultDefAdmin(MigasAdmin):
    form = make_ajax_form(FaultDef, {'attributes': 'attribute'})
    list_display = ('my_link', 'my_active', 'list_attributes', 'list_users')
    list_filter = ('active',)
    ordering = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('attributes',)

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'active', 'language', 'code')
        }),
        (_('Atributtes'), {
            'fields': ('attributes',)
        }),
        (_('Users'), {
            'fields': ('users',)
        }),
    )

    def my_link(self, object):
        return object.link()

    my_link.short_description = _("Fault Definition")

    def my_active(self, obj):
        return self.boolean_field(obj.active)

    my_active.allow_tags = True
    my_active.short_description = _('active')

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['users'].widget.can_add_related = False

        return form


@admin.register(Login)
class LoginAdmin(MigasAdmin):
    list_display = ('my_link', 'user_link', 'computer_link', 'date',)
    list_select_related = ('computer', 'user',)
    list_filter = ('date',)
    ordering = ('user', 'computer',)
    search_fields = add_computer_search_fields(
        ['user__name', 'user__fullname']
    )
    fields = ('date', 'user', 'computer_link', 'attributes')
    readonly_fields = ('date', 'user', 'computer_link', 'attributes')

    def my_link(self, object):
        return object.link()

    my_link.short_description = _("Login")

    def has_add_permission(self, request):
        return False


@admin.register(Message)
class MessageAdmin(MigasAdmin):
    list_display = ('id', 'computer_link', 'date', 'text')
    list_display_links = ('id',)
    ordering = ('-date',)
    list_filter = ('date',)
    search_fields = ('computer', 'text', 'date')
    readonly_fields = ('computer_link', 'text', 'date')
    exclude = ('computer',)


@admin.register(Migration)
class MigrationAdmin(MigasAdmin):
    list_display = ('id', 'computer_link', 'version', 'date')
    list_display_links = ('id',)
    list_select_related = ('computer', 'version')
    list_filter = ('date', 'version__platform')
    search_fields = add_computer_search_fields(['date'])
    readonly_fields = ('computer_link', 'version', 'date')
    exclude = ('computer',)
    actions = None

    def has_add_permission(self, request):
        return False


@admin.register(Notification)
class NotificationAdmin(MigasAdmin):
    list_display = ('id', 'my_checked', 'date', 'my_notification')
    list_display_links = ('id',)
    list_filter = ('checked', 'date')
    ordering = ('-date',)
    search_fields = ('date', 'notification')
    readonly_fields = ('date', 'my_notification')
    exclude = ('notification',)

    def my_checked(self, obj):
        return self.boolean_field(obj.checked)

    my_checked.allow_tags = True
    my_checked.short_description = _('checked')

    def my_notification(self, obj):
        return obj.notification

    my_notification.allow_tags = True
    my_notification.short_description = _('notification')

    actions = ['checked_ok']

    def checked_ok(self, request, queryset):
        for item in queryset:
            item.okay()

        messages.success(request, _('Checked %s') % _('Notifications'))

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

    def has_add_permission(self, request):
        return False


@admin.register(StatusLog)
class StatusLogAdmin(MigasAdmin):
    list_display = ('id', 'computer_link', 'status', 'created_at')
    list_display_links = ('id',)
    list_select_related = ('computer',)
    list_filter = ('created_at', ('status', ProductiveFilterSpec),)
    search_fields = add_computer_search_fields(['created_at'])
    readonly_fields = ('computer_link', 'status', 'created_at')
    exclude = ('computer',)
    actions = None

    def has_add_permission(self, request):
        return False


@admin.register(Update)
class UpdateAdmin(MigasAdmin):
    list_display = ('__str__', 'user', 'computer_link', 'version')
    list_display_links = ('__str__',)
    list_filter = ('date',)
    search_fields = add_computer_search_fields(['date', 'user__name'])
    readonly_fields = ('computer_link', 'user', 'version', 'date')
    exclude = ('computer',)
    actions = None


@admin.register(User)
class UserAdmin(MigasAdmin):
    list_display = ('my_link', 'fullname')
    ordering = ('name',)
    search_fields = ('name', 'fullname')
    readonly_fields = ('name', 'fullname')

    def my_link(self, object):
        return object.link()

    my_link.short_description = _("User")

    def has_add_permission(self, request):
        return False
