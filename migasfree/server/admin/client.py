# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.db.models import Prefetch
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib import admin, messages
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.shortcuts import redirect, render
from django.urls import resolve, reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html

from ajax_select.admin import AjaxSelectAdmin

from .migasfree import MigasAdmin, MigasFields

from ..filters import (
    ProductiveFilterSpec, UserFaultFilter,
    SoftwareInventoryFilter, SyncEndDateFilter,
)
from ..forms import ComputerForm, FaultDefinitionForm
from ..resources import ComputerResource
from ..models import (
    AutoCheckError, Computer, Error, Fault, FaultDefinition, Message,
    Migration, Notification, StatusLog, Synchronization, User, DeviceLogical, HwNode
)
from ..utils import strfdelta

admin.site.register(AutoCheckError)


def add_computer_search_fields(fields_list):
    for field in settings.MIGASFREE_COMPUTER_SEARCH_FIELDS:
        fields_list.append("computer__%s" % field)

    return tuple(fields_list)


@admin.register(Computer)
class ComputerAdmin(AjaxSelectAdmin, MigasAdmin):
    form = ComputerForm
    list_display = (
        'name_link',
        'status',
        'project_link',
        'sync_user_link',
        'sync_end_date',
        'hw_link',
    )
    ordering = (settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0],)
    list_filter = (
        'project__platform',
        'project',
        ('status', ProductiveFilterSpec),
        'machine',
        SoftwareInventoryFilter,
        SyncEndDateFilter,
    )
    search_fields = settings.MIGASFREE_COMPUTER_SEARCH_FIELDS + (
        'sync_user__name', 'sync_user__fullname',
    )

    readonly_fields = (
        'name',
        'fqdn',
        'uuid',
        'project_link',
        'created_at',
        'ip_address',
        'forwarded_ip_address',
        'software_inventory',
        'software_history',
        'hw_link',
        'machine',
        'cpu',
        'ram',
        'storage',
        'disks',
        'mac_address',
        'inflected_logical_devices_link',
        'sync_user_link',
        'sync_attributes_link',
        'sync_start_date',
        'sync_end_date',
        'unchecked_errors',
        'unchecked_faults',
        'last_sync_time',
    )

    fieldsets = (
        (_('General'), {
            'fields': (
                'name',
                'fqdn',
                'project_link',
                'created_at',
                'ip_address',
                'forwarded_ip_address',
            )
        }),
        (_('Current Situation'), {
            'fields': (
                'comment',
                'status',
                'tags',
            )
        }),
        (_('Devices'), {
            'fields': (
                'assigned_logical_devices_to_cid',
                'default_logical_device',
                'inflected_logical_devices_link',
            )
        }),
        (_('Synchronization'), {
            'fields': (
                'sync_user_link',
                'sync_attributes_link',
                'sync_start_date',
                'sync_end_date',
                'last_sync_time',
                'unchecked_errors',
                'unchecked_faults',
            )
        }),
        (_('Software'), {
            'fields': ('software_inventory', 'software_history',)
        }),
        (_('Hardware'), {
            'fields': (
                'last_hardware_capture',
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
    )

    resource_class = ComputerResource
    actions = ['delete_selected', 'change_status']

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(ComputerAdmin, self).get_readonly_fields(request, obj)
        if request.user.is_superuser:
            readonly_list = list(readonly_fields)
            readonly_list.remove('name')
            return tuple(readonly_list)

        return readonly_fields

    def unchecked_errors(self, obj):
        count = Error.unchecked.filter(computer__pk=obj.pk).count()
        if not count:
            return format_html(
                '<span class="label label-default">{}</span>'.format(count)
            )

        return format_html(
            '<a class="label label-danger" '
            'href="{}?computer__id__exact={}&checked__exact={}">{}</a>'.format(
                reverse('admin:server_error_changelist'),
                obj.pk,
                0,
                count
            )
        )

    unchecked_errors.short_description = _('Unchecked Errors')

    def unchecked_faults(self, obj):
        count = Fault.unchecked.filter(computer__pk=obj.pk).count()
        if not count:
            return format_html(
                '<span class="label label-default">{}</span>'.format(count)
            )

        return format_html(
            '<a class="label label-danger" '
            'href="{}?computer__id__exact={}&checked__exact={}">{}</a>'.format(
                reverse('admin:server_fault_changelist'),
                obj.pk,
                0,
                count
            )
        )

    unchecked_faults.short_description = _('Unchecked Faults')

    def last_sync_time(self, obj):
        now = datetime.now()
        delayed_time = now - timedelta(
            seconds=settings.MIGASFREE_SECONDS_MESSAGE_ALERT
        )
        is_updating = not obj.sync_end_date or obj.sync_end_date < obj.sync_start_date

        if is_updating:
            diff = now - obj.sync_start_date
        else:
            diff = obj.sync_end_date - obj.sync_start_date

        if obj.sync_start_date < delayed_time and is_updating:
            return format_html(
                '<span class="label label-warning" title="{}">'
                '<i class="fa fa-warning"></i> {}</span>'.format(
                    _('Delayed Computer'),
                    strfdelta(diff, _('{days} days, {hours:02d}:{minutes:02d}:{seconds:02d}'))
                )
            )

        if is_updating:
            return format_html(
                '<span class="label label-info">'
                '<i class="fa fa-refresh"></i> {}</span>'.format(
                    _('Updating...'),
                )
            )

        return strfdelta(diff, '{hours:02d}:{minutes:02d}:{seconds:02d}')

    last_sync_time.short_description = _('Last Update Time')

    name_link = MigasFields.link(model=Computer, name="name")
    project_link = MigasFields.link(
        model=Computer, name='project', order='project__name'
    )
    hw_link = MigasFields.objects_link(
        model=Computer, name='hwnode_set', description=_('Product')
    )
    inflected_logical_devices_link = MigasFields.objects_link(
        model=Computer, name='inflected_logical_devices'
    )
    sync_user_link = MigasFields.link(
        model=Computer, name='sync_user__name',
        description=_('User'), order="sync_user__name"
    )
    sync_attributes_link = MigasFields.objects_link(
        model=Computer, name='sync_attributes',
        description=_('sync attributes')
    )

    def delete_selected(self, request, objects):
        if not self.has_delete_permission(request):
            raise PermissionDenied

        return render(
            request,
            'computer_confirm_delete_selected.html',
            {
                'objects': [x.__str__() for x in objects],
                'ids': ', '.join([str(x.id) for x in objects])
            }
        )

    delete_selected.short_description = _("Delete selected "
                                          "%(verbose_name_plural)s")

    def change_status(self, request, objects):
        if not self.has_change_permission(request):
            raise PermissionDenied

        return render(
            request,
            'computer_change_status.html',
            {
                'objects': [x.__str__() for x in objects],
                'ids': ', '.join([str(x.id) for x in objects]),
                'status': Computer.STATUS_CHOICES
            }
        )

    change_status.short_description = _("Change status...")

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "devices_logical":
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

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "default_logical_device":
            args = resolve(request.path).args
            computer = Computer.objects.get(pk=args[0])
            kwargs['queryset'] = DeviceLogical.objects.filter(
                pk__in=[x.id for x in computer.logical_devices()]
            )
        return super(ComputerAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return super(ComputerAdmin, self).get_queryset(
            request
        ).select_related(
            "project",
            "sync_user",
            "default_logical_device",
            "default_logical_device__feature",
            "default_logical_device__device",
        ).prefetch_related(
            Prefetch('hwnode_set', queryset=HwNode.objects.filter(parent=None)),
        )


@admin.register(Error)
class ErrorAdmin(MigasAdmin):
    list_display = (
        'created_at',
        'computer_link',
        'project_link',
        'my_checked',
        'truncated_desc',
    )
    list_display_links = ('created_at',)
    list_filter = (
        'checked', 'created_at', 'project__platform',
        'project', ('computer__status', ProductiveFilterSpec),
    )
    ordering = ('-created_at', 'computer',)
    search_fields = add_computer_search_fields(['created_at', 'description'])
    readonly_fields = ('computer_link', 'project_link', 'created_at', 'description')
    exclude = ('computer', 'project')
    actions = ['checked_ok']

    my_checked = MigasFields.boolean(model=Error, name='checked')
    computer_link = MigasFields.link(
        model=Error, name='computer', order='computer__name'
    )
    project_link = MigasFields.link(
        model=Error, name='project', order='project__name'
    )

    def truncated_desc(self, obj):
        if len(obj.description) <= 250:
            return obj.description
        else:
            return obj.description[:250] + " ..."

    truncated_desc.short_description = _("Truncated error")
    truncated_desc.admin_order_field = 'error'

    def checked_ok(self, request, queryset):
        for item in queryset:
            item.checked_ok()

        messages.success(request, _('Checked %s') % _('Errors'))

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return super(ErrorAdmin, self).get_queryset(
            request
        ).select_related(
            'project',
            'computer',
        )


@admin.register(Fault)
class FaultAdmin(MigasAdmin):
    list_display = (
        'created_at',
        'computer_link',
        'project_link',
        'my_checked',
        'result',
        'fault_definition_link',
    )
    list_display_links = ('created_at',)
    list_filter = (
        UserFaultFilter, 'checked', 'created_at',
        'project__platform', 'project', 'fault_definition'
    )
    ordering = ('-created_at', 'computer',)
    search_fields = add_computer_search_fields(
        ['created_at', 'fault_definition__name', 'fault_definition__description']
    )
    readonly_fields = (
        'computer_link', 'fault_definition_link',
        'project_link', 'created_at', 'result'
    )
    exclude = ('computer', 'project', 'fault_definition')
    actions = ['checked_ok']

    my_checked = MigasFields.boolean(model=Fault, name='checked')
    computer_link = MigasFields.link(
        model=Fault, name='computer', order='computer__name'
    )
    project_link = MigasFields.link(
        model=Fault, name='project', order='project__name'
    )
    fault_definition_link = MigasFields.link(
        model=Fault, name='fault_definition', order='fault_definition__name'
    )

    def checked_ok(self, request, queryset):
        for item in queryset:
            item.checked_ok()

        messages.success(request, _('Checked %s') % _('Faults'))

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return super(FaultAdmin, self).get_queryset(
            request
        ).select_related(
            'project',
            'fault_definition',
            'computer',
        )


@admin.register(FaultDefinition)
class FaultDefinitionAdmin(MigasAdmin):
    form = FaultDefinitionForm
    list_display = (
        'name_link',
        'my_enabled',
        'included_attributes_link',
        'excluded_attributes_link',
        'users_link'
    )
    list_filter = ('enabled', 'users')
    search_fields = ('name',)
    filter_horizontal = ('included_attributes', 'excluded_attributes')

    fieldsets = (
        (_('General'), {
            'fields': ('name', 'enabled', 'description')
        }),
        (_('Code'), {
            'fields': ('language', 'code')
        }),
        (_('Attributes'), {
            'fields': ('included_attributes', 'excluded_attributes')
        }),
        (_('Users'), {
            'fields': ('users',)
        }),
    )

    name_link = MigasFields.link(model=FaultDefinition, name='name')
    my_enabled = MigasFields.boolean(model=FaultDefinition, name='enabled')
    included_attributes_link = MigasFields.objects_link(
        model=FaultDefinition, name='included_attributes',
        description=_('included attributes')
    )
    excluded_attributes_link = MigasFields.objects_link(
        model=FaultDefinition, name='excluded_attributes',
        description=_('excluded attributes')
    )
    users_link = MigasFields.objects_link(model=FaultDefinition, name='users')

    def get_queryset(self, request):
        return super(FaultDefinitionAdmin, self).get_queryset(
            request
            ).prefetch_related(
                'included_attributes',
                'included_attributes__property_att',
                'excluded_attributes',
                'excluded_attributes__property_att',
                'users',
            )


@admin.register(Message)
class MessageAdmin(MigasAdmin):
    list_display = ('updated_at', 'computer_link', 'project_link', 'user_link', 'text')
    list_display_links = ('updated_at',)
    list_select_related = ('computer',)
    list_filter = ('updated_at',)
    ordering = ('-updated_at',)
    search_fields = ('computer', 'text', 'updated_at')
    readonly_fields = ('computer_link', 'text', 'updated_at')
    exclude = ('computer',)

    computer_link = MigasFields.link(
        model=Message, name='computer', order='computer__name',
        description=_('Computer')
    )
    project_link = MigasFields.link(
        model=Message, name='computer__project', order='computer__project__name',
        description=_('Project')
    )
    user_link = MigasFields.link(
        model=Message, name='computer__sync_user', order='computer__sync_user__name',
        description=_('User')
    )

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return super(MessageAdmin, self).get_queryset(
            request
            ).prefetch_related(
                'computer__project',
                'computer__sync_user',
            )


@admin.register(Migration)
class MigrationAdmin(MigasAdmin):
    list_display = ('created_at', 'computer_link', 'project_link')
    list_display_links = ('created_at',)
    list_select_related = ('computer', 'project')
    list_filter = ('created_at', 'project__platform', 'project')
    search_fields = add_computer_search_fields(['created_at'])
    fields = ('computer_link', 'project_link', 'created_at')
    readonly_fields = ('computer_link', 'project_link', 'created_at')
    exclude = ('computer',)
    actions = None

    computer_link = MigasFields.link(
        model=Migration, name='computer', order='computer__name'
    )
    project_link = MigasFields.link(
        model=Migration, name='project', order='project__name'
    )

    def has_add_permission(self, request):
        return False


@admin.register(Notification)
class NotificationAdmin(MigasAdmin):
    list_display = ('created_at', 'my_checked', 'my_message')
    list_display_links = ('created_at',)
    list_filter = ('checked', 'created_at')
    ordering = ('-created_at',)
    search_fields = ('created_at', 'message')
    readonly_fields = ('created_at', 'my_message')
    exclude = ('message',)
    actions = ['checked_ok']

    my_checked = MigasFields.boolean(model=Notification, name='checked')
    my_message = MigasFields.text(model=Notification, name='message')

    def checked_ok(self, request, queryset):
        for item in queryset:
            item.checked_ok()

        messages.success(request, _('Checked %s') % _('Notifications'))

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

    def has_add_permission(self, request):
        return False


@admin.register(StatusLog)
class StatusLogAdmin(MigasAdmin):
    list_display = ('created_at', 'computer_link', 'status')
    list_display_links = ('created_at',)
    list_select_related = ('computer',)
    list_filter = ('created_at', ('status', ProductiveFilterSpec),)
    search_fields = add_computer_search_fields(['created_at'])
    readonly_fields = ('computer_link', 'status', 'created_at')
    exclude = ('computer',)
    actions = None

    computer_link = MigasFields.link(
        model=StatusLog, name='computer', order='computer__name'
    )

    def has_add_permission(self, request):
        return False


@admin.register(Synchronization)
class SynchronizationAdmin(MigasAdmin):
    list_display = ('created_at', 'user_link', 'computer_link', 'project_link')
    list_display_links = ('created_at',)
    list_filter = ('created_at',)
    search_fields = add_computer_search_fields(['created_at', 'user__name'])
    readonly_fields = (
        'computer_link', 'user_link', 'project_link', 'created_at',
    )
    exclude = ('computer', 'user', 'project')
    actions = None

    computer_link = MigasFields.link(
        model=Synchronization, name='computer', order='computer__name'
    )
    project_link = MigasFields.link(
        model=Synchronization, name='project', order='project__name'
    )
    user_link = MigasFields.link(model=Synchronization, name='user', order='user__name')

    def get_queryset(self, request):
        return super(SynchronizationAdmin, self).get_queryset(
            request
        ).select_related(
            'computer',
            'project',
            'user',
        )

    def has_add_permission(self, request):
        return False


@admin.register(User)
class UserAdmin(MigasAdmin):
    list_display = ('name_link', 'fullname')
    ordering = ('name',)
    search_fields = ('name', 'fullname')
    readonly_fields = ('name', 'fullname')

    name_link = MigasFields.link(model=User, name="name")

    def has_add_permission(self, request):
        return False


@admin.register(HwNode)
class HwNodeAdmin(MigasAdmin):  # TODO to hardware.py
    list_display = ('name_link',)

    name_link = MigasFields.link(model=HwNode, name='name')
