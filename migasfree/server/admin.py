# -*- coding: utf-8 -*-

"""
Admin Models
"""
from migasfree.middleware import threadlocals
from django.contrib import admin, messages
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.admin import SimpleListFilter
from django.shortcuts import redirect
from django import forms
from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models import *

from migasfree.server.views.repository import create_physical_repository
from migasfree.settings import (
    MEDIA_URL,
    MIGASFREE_COMPUTER_SEARCH_FIELDS
)

#AJAX_SELECT
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin

#WIDGETS
from migasfree.server.widgets import MigasfreeSplitDateTime
from migasfree.admin_bootstrapped.forms import *

admin.site.register(DeviceType)
admin.site.register(DeviceFeature)
admin.site.register(DeviceManufacturer)
admin.site.register(DeviceConnection)
admin.site.register(UserProfile)
admin.site.register(AutoCheckError)
admin.site.register(Platform)


class MigasAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DateTimeField: {'widget': MigasfreeSplitDateTime},
        #models.DateField: {'widget': DateInput},
        models.CharField: {'widget': TextInput},
    }


def add_computer_search_fields(fields_list):
    for field in MIGASFREE_COMPUTER_SEARCH_FIELDS:
        fields_list.append("computer__%s" % field)

    return tuple(fields_list)


def user_version(user):
    """
    Returns the user's current version
    """
    try:
        version = UserProfile.objects.get(id=user.id).version.id
    except:
        version = None

    return version


class ExtraThinTextarea(forms.Textarea):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', {})
        attrs.setdefault('cols', 20)
        attrs.setdefault('rows', 1)
        super(ExtraThinTextarea, self).__init__(*args, **kwargs)


class VersionAdmin(MigasAdmin):
    list_display = ('name', 'platform', 'pms', 'computerbase', 'autoregister')
    actions = None

admin.site.register(Version, VersionAdmin)


class MigrationAdmin(MigasAdmin):
    list_display = ('id', 'computer_link', 'version_link', 'date')
    list_filter = ('date', 'version__platform', )
    search_fields = add_computer_search_fields(['date'])
    readonly_fields = ('computer_link', 'version', 'date')
    exclude = ("computer",)
    actions = None

admin.site.register(Migration, MigrationAdmin)


class UpdateAdmin(MigasAdmin):
    list_display = ('id', 'computer_link', 'user', 'date', 'version')
    list_filter = ('date', )
    search_fields = add_computer_search_fields(['date', 'user__name'])
    readonly_fields = ('computer_link', 'user', 'version', 'date')
    exclude = ('computer',)
    actions = None

admin.site.register(Update, UpdateAdmin)


class CheckingAdmin(MigasAdmin):
    list_display = ('name', 'active', 'alert')
    list_filter = ('active', )

admin.site.register(Checking, CheckingAdmin)


class DeviceDriverAdmin(MigasAdmin):
    list_display = ('id', 'model', 'version', 'feature')

admin.site.register(DeviceDriver, DeviceDriverAdmin)


class DeviceLogicalForm(forms.ModelForm):
    x = make_ajax_form(Computer, {'devices_logical': 'computer'})

    computers = x.devices_logical
    computers.label =_('Computers')

    class Meta:
        model = DeviceLogical

    def __init__(self, *args, **kwargs):
        super(DeviceLogicalForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            lst = []
            for computer in self.instance.computer_set.all():
                lst.append(computer.id)
            self.fields['computers'].initial = lst

    def save(self, commit=True):
        instance=forms.ModelForm.save(self, False)
        old_save_m2m = self.save_m2m
        def save_m2m():
            old_save_m2m()
            instance.computer_set.clear()
            for computer in self.cleaned_data['computers']:
                instance.computer_set.add(computer)

        self.save_m2m = save_m2m
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class DeviceLogicalAdmin(admin.ModelAdmin):
    form = DeviceLogicalForm
    fields = ("device", "feature", "computers")

admin.site.register(DeviceLogical, DeviceLogicalAdmin)


class DeviceLogicalInline(admin.TabularInline):
    model = DeviceLogical
    form = DeviceLogicalForm
    fields = ( "feature", "computers")

    extra = 0


class DeviceAdmin(MigasAdmin):
    list_display = (
        'name',
        'model',
    )
    list_filter = ('model',)
    search_fields = (
        'name',
        'model__name',
        'model__manufacturer__name'
    )
    fields = (
        'name',
        'model',
        'connection',
        'data',
    )

    inlines = [DeviceLogicalInline, ]

    class Media:
        js = ('js/device_admin.js',)

admin.site.register(Device, DeviceAdmin)


class DeviceDriverInline(admin.TabularInline):
    model = DeviceDriver
    formfield_overrides = {models.TextField: {'widget': ExtraThinTextarea}}
    fields = ('version', 'feature', 'name', 'install')
    ordering = ['version', 'feature']


class DeviceModelAdmin(MigasAdmin):
    list_display = ('name', 'manufacturer', 'devicetype')
    list_filter = ('devicetype', 'manufacturer')
    search_fields = (
        'name',
        'manufacturer__name',
        'connections__devicetype__name'
    )
    inlines = [DeviceDriverInline, ]


admin.site.register(DeviceModel, DeviceModelAdmin)


class PmsAdmin(MigasAdmin):
    list_display = ('name',)

admin.site.register(Pms, PmsAdmin)


class StoreAdmin(MigasAdmin):
    list_display = ('link',)
    search_fields = ('name',)

admin.site.register(Store, StoreAdmin)


class PropertyAdmin(MigasAdmin):
    list_display = ('prefix', 'name', 'active', 'kind', 'auto',)
    list_filter = ('active',)
    ordering = ('name',)
    search_fields = ('name', 'prefix',)
    actions = None

admin.site.register(Property, PropertyAdmin)


class AttributeAdmin(MigasAdmin):
    list_display = ('link', 'value', 'description', 'property_link',)
    list_filter = ('property_att',)
    ordering = ('property_att', 'value',)
    search_fields = ('value', 'description')

admin.site.register(Attribute, AttributeAdmin)


class LoginAdmin(MigasAdmin):
    form = make_ajax_form(Login, {'attributes': 'attribute'})

    list_display = ('id', 'user_link', 'computer_link', 'date',)
    list_filter = ('date',)
    ordering = ('user', 'computer',)
    search_fields = add_computer_search_fields(
        ['user__name', 'user__fullname']
    )

    fieldsets = (
        (None, {
            'fields': ('date', 'user', 'computer_link', 'attributes')
        }),
    )
    readonly_fields = ('date', 'user', 'computer_link', 'attributes')


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


class UserAdmin(MigasAdmin):
    list_display = ('name', 'fullname',)
    ordering = ('name',)
    search_fields = ('name', 'fullname')
    readonly_fields = ('name', 'fullname')

admin.site.register(User, UserAdmin)


class NotificationAdmin(MigasAdmin):
    list_display = (
        'id',
        'checked',
        'date',
        'notification',
    )
    list_filter = ('checked', 'date')
    ordering = ('date',)
    search_fields = ('date', 'notification',)
    readonly_fields = ('date', 'notification',)

    actions = ['checked_ok']

    def checked_ok(self, request, queryset):
        for noti in queryset:
            noti.checked = True
            noti.save()

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

admin.site.register(Notification, NotificationAdmin)


class ErrorAdmin(MigasAdmin):
    list_display = (
        'id',
        'computer_link',
        'version',
        'checked',
        'date',
        'truncate_error',
    )
    list_filter = ('checked', 'date', "version")
    #list_editable = ('checked',)  # TODO
    ordering = ('date', 'computer',)
    search_fields = add_computer_search_fields(['date', 'error'])
    readonly_fields = ('computer_link','version','date','error')
    exclude = ('computer',)

    actions = ['checked_ok']

    def checked_ok(self, request, queryset):
        for error in queryset:
            error.checked = True
            error.save()

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

admin.site.register(Error, ErrorAdmin)


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
        lst = [threadlocals.get_current_user().id]
        if self.value() == 'me':
            return queryset.filter(Q(faultdef__users__id__in=lst) | Q(faultdef__users=None))
        elif self.value() == 'only_me':
            return queryset.filter(Q(faultdef__users__id__in=lst))
        elif self.value() == 'others':
            return queryset.exclude(faultdef__users__id__in=lst).exclude(faultdef__users=None)
        elif self.value() == 'no_assign':
            return queryset.filter(Q(faultdef__users=None))


class FaultAdmin(MigasAdmin):
    list_display = (
        'id',
        'computer_link',
        'version',
        'checked',
        'date',
        'text',
        'faultdef',
        'list_users'
    )
    list_filter = (UserFaultFilter, 'checked', 'date', 'version', 'faultdef')
    ordering = ('date', 'computer',)
    search_fields = add_computer_search_fields(['date', 'faultdef__name'])
    readonly_fields = ('computer_link','faultdef','version','date','text')
    exclude = ('computer',)

    actions = ['checked_ok']

    def checked_ok(self, request, queryset):
        for fault in queryset:
            fault.checked = True
            fault.save()

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

admin.site.register(Fault, FaultAdmin)


class FaultDefAdmin(MigasAdmin):
    form = make_ajax_form(FaultDef, {'attributes': 'attribute'})
    list_display = ('name', 'active', 'list_attributes', 'list_users')
    list_filter = ('active',)
    ordering = ('name',)
    search_fields = ('name', 'function',)
    filter_horizontal = ('attributes',)

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'active', 'language', 'code')
        }),
        (_('Atributtes'), {
            'classes': ('collapse',),
            'fields': ('attributes',)
        }),
        (_('Users'), {
            'classes': ('collapse',),
            'fields': ('users',)
        }),
    )

admin.site.register(FaultDef, FaultDefAdmin)


class ComputerAdmin(AjaxSelectAdmin, MigasAdmin):
    form = make_ajax_form(Computer, {
        'devices_logical': 'devicelogical',
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
    )

    fieldsets = (
        (_('General'), {
            'fields': (
                'uuid',
                'version',
                'dateinput',
                'datelastupdate',
                'ip',
                'datehardware',
                'hw_link',
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

    def formfield_for_manytomany(self, db_field, request, **kwargs):
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

admin.site.register(Computer, ComputerAdmin)


class MessageAdmin(MigasAdmin):
    list_display = ('id', 'computer_link', 'date', 'text',)
    ordering = ('date',)
    list_filter = ('date',)
    search_fields = ('computer', 'text', 'date',)
    readonly_fields = ('computer_link', 'text', 'date')
    exclude = ('computer',)

admin.site.register(Message, MessageAdmin)


class MessageServerAdmin(MigasAdmin):
    list_display = ('id', 'date', 'text',)
    ordering = ('date',)
    list_filter = ('date',)
    search_fields = ('text', 'date',)
    readonly_fields = ('text', 'date')

admin.site.register(MessageServer, MessageServerAdmin)


class RepositoryAdmin(AjaxSelectAdmin, MigasAdmin):
    form = make_ajax_form(Repository, {
        'attributes': 'attribute',
        'packages': 'package',
        'excludes': 'attribute'
    })

    list_display = ('name', 'active', 'date', 'timeline',)
    list_filter = ('active',)
    ordering = ('name',)
    search_fields = ('name', 'packages__name',)
    actions = None

    fieldsets = (
        (_('General'), {
            'fields': ('name', 'version', 'active', 'comment',)
        }),
        (_('Schedule'), {
            'fields': ('date', 'schedule',)
        }),
        (_('Packages'), {
            'classes': ('collapse',),
            'fields': ('packages', 'toinstall', 'toremove',)
        }),
        (_('Default'), {
            'classes': ('collapse',),
            'fields': (
                'defaultpreinclude',
                'defaultinclude',
                'defaultexclude',
            )
        }),
        (_('Atributtes'), {
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

            return db_field.formfield(**kwargs)

        if db_field.name == "attributes":
            kwargs["queryset"] = Attribute.objects.filter(
                property_att__active=True
            )

            return db_field.formfield(**kwargs)

        return super(RepositoryAdmin, self).formfield_for_manytomany(
            db_field,
            request,
            **kwargs
        )

    def save_model(self, request, obj, form, change):
        super(RepositoryAdmin, self).save_model(request, obj, form, change)

        # create physical repository  when packages is change or not have packages
        if "packages" in form.changed_data or len(form.cleaned_data['packages']) == 0:
            messages.add_message(
                request,
                messages.INFO,
                create_physical_repository(obj, form.cleaned_data['packages'])
            )

admin.site.register(Repository, RepositoryAdmin)


class ScheduleDelayline(admin.TabularInline):
    model = ScheduleDelay
    form = make_ajax_form(ScheduleDelay, {'attributes': 'attribute'})
    extra = 0
    ordering = ('delay',)


class ScheduleAdmin(MigasAdmin):
    list_display = ('name', 'description',)
    inlines = [ScheduleDelayline, ]
    extra = 0

admin.site.register(Schedule, ScheduleAdmin)


class PackageAdmin(MigasAdmin):
    list_display = ('link', 'store',)
    list_filter = ('store',)
    search_fields = ('name', 'store__name',)
    ordering = ('name',)

admin.site.register(Package, PackageAdmin)


class QueryAdmin(MigasAdmin):
    list_display = ('name', 'description',)
    actions = ['run_query']

    def run_query(self, request, queryset):
        for query in queryset:
            return redirect(reverse('query', args=(query.id, )))

    run_query.short_description = _("Run Query")

admin.site.register(Query, QueryAdmin)
