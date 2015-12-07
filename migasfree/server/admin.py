## -*- coding: utf-8 -*-

from django.contrib import admin, messages
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.shortcuts import redirect, render
from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext, ugettext_lazy as _
from django.conf import settings

from .models import *

from .tasks import (
    create_physical_repository,
    remove_physical_repository
)

from .functions import compare_values
from .filters import (
    ProductiveFilterSpec, TagFilter, AttributeFilter, UserFaultFilter
)
from .forms import (
    RepositoryForm, DeviceLogicalForm, PropertyForm,
    TagForm, ComputerForm, ExtraThinTextarea
)

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin

admin.site.register(AutoCheckError)

sql_total_computer = "SELECT COUNT(server_login.id) \
    FROM server_login,server_login_attributes  \
    WHERE server_attribute.id=server_login_attributes.attribute_id \
    and server_login_attributes.login_id=server_login.id"


class MigasAdmin(admin.ModelAdmin):
    def boolean_field(self, field):
        if field:
            ret = '<span class="fa fa-check boolean-yes">' \
                + '<span class="sr-only">%s</span></span>' % ugettext('Yes')
        else:
            ret = '<span class="fa fa-times boolean-no">' \
                + '<span class="sr-only">%s</span></span>' % ugettext('No')

        return ret


def add_computer_search_fields(fields_list):
    for field in settings.MIGASFREE_COMPUTER_SEARCH_FIELDS:
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


@admin.register(Platform)
class PlatformAdmin(MigasAdmin):
    list_display = ('my_link',)

    def my_link(self, object):
        return object.link()

    my_link.short_description = _("Platform")


@admin.register(UserProfile)
class UserProfileAdmin(MigasAdmin):
    list_display = ('my_link',)

    def my_link(self, object):
        return object.link()

    my_link.short_description = _("User Profile")

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['version'].widget.can_add_related = False
        form.base_fields['groups'].widget.can_add_related = False

        return form


@admin.register(Version)
class VersionAdmin(MigasAdmin):
    list_display = (
        'link',
        'platform',
        'pms',
        'computerbase',
        'my_autoregister'
    )
    actions = None

    def my_autoregister(self, obj):
        return self.boolean_field(obj.autoregister)

    my_autoregister.allow_tags = True
    my_autoregister.short_description = _('autoregister')

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['pms'].widget.can_add_related = False
        form.base_fields['platform'].widget.can_add_related = False

        return form


@admin.register(Migration)
class MigrationAdmin(MigasAdmin):
    list_display = ('id', 'computer_link', 'version', 'date')
    list_select_related = ('computer', 'version',)
    list_filter = ('date', 'version__platform',)
    search_fields = add_computer_search_fields(['date'])
    readonly_fields = ('computer_link', 'version', 'date')
    exclude = ("computer",)
    actions = None

    def has_add_permission(self, request):
        return False


@admin.register(StatusLog)
class StatusLogAdmin(MigasAdmin):
    list_display = ('id', 'computer_link', 'status', 'created_at')
    list_select_related = ('computer', )
    list_filter = ('created_at', ('status', ProductiveFilterSpec),)
    search_fields = add_computer_search_fields(['created_at'])
    readonly_fields = ('computer_link', 'status', 'created_at')
    exclude = ("computer",)
    actions = None

    def has_add_permission(self, request):
        return False


@admin.register(Update)
class UpdateAdmin(MigasAdmin):
    list_display = ('id', 'computer_link', 'user', 'date', 'version')
    list_filter = ('date', )
    search_fields = add_computer_search_fields(['date', 'user__name'])
    readonly_fields = ('computer_link', 'user', 'version', 'date')
    exclude = ('computer',)
    actions = None


@admin.register(Checking)
class CheckingAdmin(MigasAdmin):
    list_display = ('name', 'my_active', 'my_alert')
    list_filter = ('active',)

    def my_active(self, obj):
        return self.boolean_field(obj.active)

    my_active.allow_tags = True
    my_active.short_description = _('active')

    def my_alert(self, obj):
        return self.boolean_field(obj.alert)

    my_alert.allow_tags = True
    my_alert.short_description = _('alert')


@admin.register(DeviceType)
class DeviceTypeAdmin(MigasAdmin):
    ordering = ('name',)


@admin.register(DeviceFeature)
class DeviceFeatureAdmin(MigasAdmin):
    ordering = ('name',)


@admin.register(DeviceManufacturer)
class DeviceManufacturerAdmin(MigasAdmin):
    ordering = ('name',)


@admin.register(DeviceConnection)
class DeviceConnectionAdmin(admin.ModelAdmin):
    list_select_related = ('devicetype',)
    ordering = ('devicetype__name', 'name')

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['devicetype'].widget.can_add_related = False

        return form


@admin.register(DeviceDriver)
class DeviceDriverAdmin(MigasAdmin):
    list_display = ('id', 'model', 'version', 'feature')

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['model'].widget.can_add_related = False
        form.base_fields['version'].widget.can_add_related = False
        form.base_fields['feature'].widget.can_add_related = False

        return form


@admin.register(DeviceLogical)
class DeviceLogicalAdmin(MigasAdmin):
    form = DeviceLogicalForm
    fields = ("device", "feature", "computers")
    list_select_related = ('device', 'feature',)
    list_display = (
        'link',
        'device_link',
        'feature',
    )
    ordering = ('device__name', 'feature__name')
    search_fields = (
        'id',
        'device__name',
        'device__model__name',
        'device__model__manufacturer__name',
        'feature__name',
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['device'].widget.can_add_related = False
        form.base_fields['feature'].widget.can_add_related = False

        return form


class DeviceLogicalInline(admin.TabularInline):
    model = DeviceLogical
    form = DeviceLogicalForm
    fields = ("feature", "computers")

    extra = 0


@admin.register(Device)
class DeviceAdmin(MigasAdmin):
    list_display = (
        'name',
        'model_link',
        'connection'
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
    ordering = ['name', ]

    inlines = [DeviceLogicalInline]

    class Media:
        js = ('js/device_admin.js',)

    def save_related(self, request, form, formsets, change):
        super(type(self), self).save_related(request, form, formsets, change)
        device = form.instance

        for feature in DeviceFeature.objects.filter(
            devicedriver__model__id=device.model.id
        ).distinct():
            if DeviceLogical.objects.filter(
                Q(device__id=device.id) & Q(feature=feature)
            ).count() == 0:
                logical = device.devicelogical_set.create(
                    device=device,
                    feature=feature
                )
                logical.save()

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['model'].widget.can_add_related = False
        form.base_fields['connection'].widget.can_add_related = False

        return form


class DeviceDriverInline(admin.TabularInline):
    model = DeviceDriver
    formfield_overrides = {models.TextField: {'widget': ExtraThinTextarea}}
    fields = ('version', 'feature', 'name', 'install')
    ordering = ['version', 'feature']


@admin.register(DeviceModel)
class DeviceModelAdmin(MigasAdmin):
    list_display = ('name', 'manufacturer', 'devicetype')
    list_filter = ('devicetype', 'manufacturer')
    ordering = ('devicetype__name', 'manufacturer__name', 'name',)
    search_fields = (
        'name',
        'manufacturer__name',
        'connections__devicetype__name'
    )
    inlines = [DeviceDriverInline, ]

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['manufacturer'].widget.can_add_related = False
        form.base_fields['devicetype'].widget.can_add_related = False
        form.base_fields['connections'].widget.can_add_related = False

        return form


@admin.register(Pms)
class PmsAdmin(MigasAdmin):
    list_display = ('my_link',)

    def my_link(self, object):
        return object.link()

    my_link.short_description = _("Package Management System")


@admin.register(Store)
class StoreAdmin(MigasAdmin):
    list_display = ('my_link',)
    search_fields = ('name',)

    def my_link(self, object):
        return object.link()

    my_link.short_description = _("Store")

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['version'].widget.can_add_related = False

        return form


@admin.register(Property)
class PropertyAdmin(MigasAdmin):
    list_display = ('my_link', 'my_active', 'kind', 'my_auto')
    list_filter = ('active',)
    ordering = ('name',)
    search_fields = ('name', 'prefix')
    form = PropertyForm
    fields = (
        'prefix', 'name', 'active',
        'language', 'code', 'kind', 'auto',
    )
    actions = None

    def my_link(self, object):
        return object.link()

    my_link.short_description = _("Property")

    def my_active(self, obj):
        return self.boolean_field(obj.active)

    my_active.allow_tags = True
    my_active.short_description = _('active')

    def my_auto(self, obj):
        return self.boolean_field(obj.auto)

    my_auto.allow_tags = True
    my_auto.short_description = _('auto')

    def queryset(self, request):
        return self.model.objects.filter(tag=False)


@admin.register(TagType)
class TagTypeAdmin(MigasAdmin):
    list_display = ('my_link', 'prefix', 'my_active')
    fields = ('prefix', 'name', 'kind', 'active')

    def my_link(self, object):
        return object.link()

    my_link.short_description = _("Tag Type")

    def my_active(self, obj):
        return self.boolean_field(obj.active)

    my_active.allow_tags = True
    my_active.short_description = _('active')

    def queryset(self, request):
        return self.model.objects.filter(tag=True)


@admin.register(Attribute)
class AttributeAdmin(MigasAdmin):
    list_display = (
        'my_link', 'description', 'total_computers', 'property_link'
    )
    list_select_related = ('property_att',)
    list_filter = (AttributeFilter,)
    ordering = ('property_att', 'value',)
    search_fields = ('value', 'description')
    readonly_fields = ('property_att', 'value',)

    def my_link(self, object):
        return object.link()

    my_link.short_description = _("Attribute")

    def queryset(self, request):
        return self.model.objects.filter(property_att__tag=False).extra(
            select={'total_computers': sql_total_computer}
        )

    def has_add_permission(self, request):
        return False


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    form = TagForm
    list_display = ('my_link', 'description', 'total_computers', 'property_att')
    fields = ('property_att', 'value', 'description', 'computers')
    list_filter = (TagFilter,)
    ordering = ('property_att', 'value',)
    search_fields = ('value', 'description')

    def my_link(self, object):
        return object.link()

    my_link.short_description = _("Tag")

    def queryset(self, request):
        return self.model.objects.filter(property_att__tag=True).extra(
            select={'total_computers': sql_total_computer}
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['property_att'].widget.can_add_related = False

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


@admin.register(Notification)
class NotificationAdmin(MigasAdmin):
    list_display = (
        'id',
        'my_checked',
        'date',
        'notification',
    )
    list_filter = ('checked', 'date')
    ordering = ('-date',)
    search_fields = ('date', 'notification',)
    readonly_fields = ('date', 'notification',)

    def my_checked(self, obj):
        return self.boolean_field(obj.checked)

    my_checked.allow_tags = True
    my_checked.short_description = _('checked')

    actions = ['checked_ok']

    def checked_ok(self, request, queryset):
        for noti in queryset:
            noti.okay()

        messages.success(request, _('Checked %s') % _('Notifications'))

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

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
        for error in queryset:
            error.okay()

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
        for fault in queryset:
            fault.okay()

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
    search_fields = ('name', 'function',)
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
    )

    fieldsets = (
        (_('General'), {
            'fields': (
                'uuid',
                'name',
                'version',
                'status',
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

    actions = ['delete_selected']

    def my_link(self, object):
        return object.link()

    my_link.short_description = _('Computer')

    def delete_selected(self, request, objects):
        if not self.has_delete_permission(request):
            raise PermissionDenied

        _list = []
        for obj in objects:
            _list.append(obj.__str__())

        return render(
            request,
            'computer_confirm_delete_selected.html',
            {'object_list': ', '.join(_list)}
        )

    delete_selected.short_description = _("Delete selected "
        "%(verbose_name_plural)s")

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


@admin.register(Message)
class MessageAdmin(MigasAdmin):
    list_display = ('id', 'computer_link', 'date', 'text',)
    ordering = ('-date',)
    list_filter = ('date',)
    search_fields = ('computer', 'text', 'date',)
    readonly_fields = ('computer_link', 'text', 'date')
    exclude = ('computer',)


@admin.register(MessageServer)
class MessageServerAdmin(MigasAdmin):
    list_display = ('id', 'date', 'text',)
    ordering = ('-date',)
    list_filter = ('date',)
    search_fields = ('text', 'date',)
    readonly_fields = ('text', 'date')


@admin.register(Repository)
class RepositoryAdmin(AjaxSelectAdmin, MigasAdmin):
    form = RepositoryForm

    list_display = ('my_link', 'my_active', 'date', 'timeline')
    list_select_related = ('schedule',)
    list_filter = ('active',)
    ordering = ('name',)
    search_fields = ('name', 'packages__name')
    actions = None

    fieldsets = (
        (_('General'), {
            'fields': ('name', 'version', 'active', 'comment',)
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
            'fields': ('attributes', 'excludes')
        }),
        (_('Schedule'), {
            'fields': ('date', 'schedule',)
        }),
    )

    def my_link(self, object):
        return object.link()

    my_link.short_description = _("Repository")

    def my_active(self, obj):
        return self.boolean_field(obj.active)

    my_active.allow_tags = True
    my_active.short_description = _('active')

    # QuerySet filter by user version
    def queryset(self, request):
        if request.user.is_superuser:
            return self.model._default_manager.get_queryset()
        else:
            return self.model._default_manager.get_queryset().filter(
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

        return super(type(self), self).formfield_for_manytomany(
            db_field,
            request,
            **kwargs
        )

    def save_model(self, request, obj, form, change):
        is_new = (obj.pk is None)
        packages_after = form.cleaned_data['packages']
        super(type(self), self).save_model(request, obj, form, change)

        name_old = "%s" % form.initial.get('name')
        name_new = "%s" % obj.name

        # create physical repository when packages has been changed
        # or repository not have packages at first time
        # or name is changed (to avoid client errors)
        if ((is_new and len(packages_after) == 0)
                or compare_values(
                    obj.packages.values_list('id', flat=True),  # pkgs before
                    packages_after
                ) is False) or (name_new != name_old):
            create_physical_repository(request, obj, packages_after)

            # delete old repository by name changed
            if name_new != name_old and not is_new:
                remove_physical_repository(request, obj, name_old)

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['version'].widget.can_add_related = False
        form.base_fields['schedule'].widget.can_add_related = False

        return form


class ScheduleDelayline(admin.TabularInline):
    model = ScheduleDelay
    fields = ('delay', 'attributes', 'total_computers', 'duration')
    form = make_ajax_form(ScheduleDelay, {'attributes': 'attribute_computers'})
    extra = 0
    ordering = ('delay',)
    readonly_fields = ('total_computers',)


@admin.register(Schedule)
class ScheduleAdmin(MigasAdmin):
    list_display = ('my_link', 'description',)
    inlines = [ScheduleDelayline, ]
    extra = 0

    def my_link(self, object):
        return object.link()

    my_link.short_description = _("Schedule")


@admin.register(Package)
class PackageAdmin(MigasAdmin):
    list_display = ('my_link', 'store',)
    list_filter = ('store',)
    list_per_page = 25
    search_fields = ('name', 'store__name',)
    ordering = ('name',)

    def my_link(self, object):
        return object.link()

    my_link.short_description = _("Package/Set")

    def get_form(self, request, obj=None, **kwargs):
        form = super(type(self), self).get_form(request, obj, **kwargs)
        form.base_fields['version'].widget.can_add_related = False
        form.base_fields['store'].widget.can_add_related = False

        return form


@admin.register(Query)
class QueryAdmin(MigasAdmin):
    list_display = ('name', 'description',)
    actions = ['run_query']

    def run_query(self, request, queryset):
        for query in queryset:
            return redirect(reverse('query', args=(query.id, )))

    run_query.short_description = _("Run Query")


@admin.register(AttributeSet)
class AttributeSetAdmin(MigasAdmin):
    form = make_ajax_form(
        AttributeSet,
        {'attributes': 'attribute', 'excludes': 'attribute'}
    )
    list_display = ('name',)
