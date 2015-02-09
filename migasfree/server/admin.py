# -*- coding: utf-8 -*-

"""
Admin Models
"""
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.admin import SimpleListFilter
from django.shortcuts import redirect, render
from django import forms
from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from migasfree.middleware import threadlocals
from migasfree.server.models import *
from migasfree.server.views.repository import create_physical_repository, remove_physical_repository

from .functions import compare_values, trans

#AJAX_SELECT
from ajax_select import make_ajax_form, make_ajax_field
from ajax_select.admin import AjaxSelectAdmin

#WIDGETS
from migasfree.server.widgets import MigasfreeSplitDateTime
from migasfree.admin_bootstrapped.forms import *

admin.site.register(DeviceType)
admin.site.register(DeviceFeature)
admin.site.register(DeviceManufacturer)
admin.site.register(AutoCheckError)


class MigasAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DateTimeField: {'widget': MigasfreeSplitDateTime},
        #models.DateField: {'widget': DateInput},
        models.CharField: {'widget': TextInput},
    }

    def boolean_field(self, field):
        if field:
            ret = '<span class="fa fa-check boolean-yes">' \
                + '<span class="sr-only">%s</span></span>' % trans('Yes')
        else:
            ret = '<span class="fa fa-times boolean-no">' \
                + '<span class="sr-only">%s</span></span>' % trans('No')

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


class ExtraThinTextarea(forms.Textarea):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', {})
        attrs.setdefault('cols', 20)
        attrs.setdefault('rows', 1)
        super(ExtraThinTextarea, self).__init__(*args, **kwargs)


class PlatformAdmin(MigasAdmin):
    list_display = ("link",)

admin.site.register(Platform, PlatformAdmin)


class UserProfileAdmin(MigasAdmin):
    list_display = ("link",)

admin.site.register(UserProfile, UserProfileAdmin)


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

admin.site.register(Version, VersionAdmin)


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
    list_display = ('name', 'my_active', 'my_alert')
    list_filter = ('active', )

    def my_active(self, obj):
        return self.boolean_field(obj.active)

    my_active.allow_tags = True
    my_active.short_description = _('active')

    def my_alert(self, obj):
        return self.boolean_field(obj.alert)

    my_alert.allow_tags = True
    my_alert.short_description = _('alert')

admin.site.register(Checking, CheckingAdmin)


class DeviceConnectionAdmin(admin.ModelAdmin):
    list_select_related = ('devicetype',)

admin.site.register(DeviceConnection, DeviceConnectionAdmin)


class DeviceDriverAdmin(MigasAdmin):
    list_display = ('id', 'model', 'version', 'feature')

admin.site.register(DeviceDriver, DeviceDriverAdmin)


class DeviceLogicalForm(forms.ModelForm):
    x = make_ajax_form(Computer, {'devices_logical': 'computer'})

    computers = x.devices_logical
    computers.label = _('Computers')

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
        instance = forms.ModelForm.save(self, False)
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


class DeviceLogicalAdmin(MigasAdmin):
    form = DeviceLogicalForm
    fields = ("device", "feature", "computers")
    list_select_related = ('device', 'feature',)
    list_display = ('link', 'feature')

admin.site.register(DeviceLogical, DeviceLogicalAdmin)


class DeviceLogicalInline(admin.TabularInline):
    model = DeviceLogical
    form = DeviceLogicalForm
    fields = ("feature", "computers")

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
    list_display = ('link',)

admin.site.register(Pms, PmsAdmin)


class StoreAdmin(MigasAdmin):
    list_display = ('link',)
    search_fields = ('name',)

admin.site.register(Store, StoreAdmin)


class PropertyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PropertyForm, self).__init__(*args, **kwargs)

        self.fields['code'].required = True

    class Meta:
        model = Property


class PropertyAdmin(MigasAdmin):
    list_display = ('link', 'my_active', 'kind', 'my_auto',)
    list_filter = ('active',)
    ordering = ('name',)
    search_fields = ('name', 'prefix',)
    form = PropertyForm
    fields = (
        'prefix', 'name', 'active',
        'language', 'code', 'kind', 'auto',
    )
    actions = None

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

admin.site.register(Property, PropertyAdmin)


class TagTypeAdmin(MigasAdmin):
    list_display = ('link', 'prefix', 'my_active')
    fields = ('prefix', 'name', 'kind','active')

    def my_active(self, obj):
        return self.boolean_field(obj.active)

    my_active.allow_tags = True
    my_active.short_description = _('active')

    def queryset(self, request):
        return self.model.objects.filter(tag=True)

admin.site.register(TagType, TagTypeAdmin)


class AttributeFilter(SimpleListFilter):
    title = 'Attribute'
    parameter_name = 'Attribute'

    def lookups(self, request, model_admin):
        return [(c.id, c.name) for c in Property.objects.filter(tag=False)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(property_att__id__exact=self.value())
        else:
            return queryset


class AttAdmin(MigasAdmin):
    list_display = ('link', 'description', 'property_link',)
    list_select_related = ('property_att',)
    list_filter = (AttributeFilter,)
    ordering = ('property_att', 'value',)
    search_fields = ('value', 'description')
    readonly_fields = ('property_att', 'value',)

admin.site.register(Att, AttAdmin)


class AttributeAdmin(AttAdmin, MigasAdmin):
    def queryset(self, request):
        return self.model.objects.filter(property_att__tag=False)

    def has_add_permission(self, request):
        return False

admin.site.register(Attribute, AttributeAdmin)


class TagFilter(SimpleListFilter):
    title = 'Tag'
    parameter_name = 'Tag'

    def lookups(self, request, model_admin):
        return [(c.id, c.name) for c in Property.objects.filter(tag=True)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(property_att__id__exact=self.value())
        else:
            return queryset


class TagForm(forms.ModelForm):
    x = make_ajax_form(Computer, {'tags': 'computer'})

    computers = x.tags
    computers.label = _('Computers')

    class Meta:
        model = Tag

    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            lst = []
            for computer in self.instance.computer_set.all():
                lst.append(computer.id)
            self.fields['computers'].initial = lst

        self.fields['property_att'].queryset = Property.objects.filter(tag=True)

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)
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


class TagAdmin(admin.ModelAdmin):
    form = TagForm
    list_display = ('link', 'description', 'property_att')
    fields = ('property_att', 'value', 'description', 'computers')
    list_select_related = ('tag_att',)
    list_filter = (TagFilter,)
    ordering = ('property_att', 'value',)
    search_fields = ('value', 'description')
    def queryset(self, request):
        return self.model.objects.filter(property_att__tag=True)

admin.site.register(Tag, TagAdmin)



class LoginAdmin(MigasAdmin):
    form = make_ajax_form(Login, {'attributes': 'attribute'})

    list_display = ('link', 'user_link', 'computer_link', 'date',)
    list_select_related = ('computer', 'user',)
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
            return db_field.formfield(**kwargs)

        return super(LoginAdmin, self).formfield_for_manytomany(
            db_field,
            request,
            **kwargs
        )

    def has_add_permission(self, request):
        return False

admin.site.register(Login, LoginAdmin)


class UserAdmin(MigasAdmin):
    list_display = ('link', 'fullname',)
    ordering = ('name',)
    search_fields = ('name', 'fullname')
    readonly_fields = ('name', 'fullname')

    def has_add_permission(self, request):
        return False

admin.site.register(User, UserAdmin)


class NotificationAdmin(MigasAdmin):
    list_display = (
        'id',
        'my_checked',
        'date',
        'notification',
    )
    list_filter = ('checked', 'date')
    ordering = ('date',)
    search_fields = ('date', 'notification',)
    readonly_fields = ('date', 'notification',)

    def my_checked(self, obj):
        return self.boolean_field(obj.checked)

    my_checked.allow_tags = True
    my_checked.short_description = _('checked')

    actions = ['checked_ok']

    def checked_ok(self, request, queryset):
        for noti in queryset:
            noti.checked = True
            noti.save()

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

    def has_add_permission(self, request):
        return False

admin.site.register(Notification, NotificationAdmin)


class ErrorAdmin(MigasAdmin):
    list_display = (
        'id',
        'computer_link',
        'version',
        'my_checked',
        'date',
        'truncate_error',
    )
    list_filter = ('checked', 'date', "version")
    #list_editable = ('checked',)  # TODO
    ordering = ('date', 'computer',)
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
            error.checked = True
            error.save()

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

    def has_add_permission(self, request):
        return False

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
    list_filter = (UserFaultFilter, 'checked', 'date', 'version', 'faultdef')
    ordering = ('date', 'computer',)
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
            fault.checked = True
            fault.save()

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

    def has_add_permission(self, request):
        return False

admin.site.register(Fault, FaultAdmin)


class FaultDefAdmin(MigasAdmin):
    form = make_ajax_form(FaultDef, {'attributes': 'attribute'})
    list_display = ('link', 'my_active', 'list_attributes', 'list_users')
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

    def my_active(self, obj):
        return self.boolean_field(obj.active)

    my_active.allow_tags = True
    my_active.short_description = _('active')

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
    list_per_page = 25
    ordering = ('name',)
    list_filter = ('version',)
    search_fields = settings.MIGASFREE_COMPUTER_SEARCH_FIELDS

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

    actions = ['delete_selected']

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

    delete_selected.short_description = _("Delete selected %(verbose_name_plural)s")

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

    def has_add_permission(self, request):
        return False

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


class RepositoryForm(forms.ModelForm):
    attributes = make_ajax_field(Repository, 'attributes', 'attribute')
    packages = make_ajax_field(Repository, 'packages', 'package')
    excludes = make_ajax_field(Repository, 'excludes', 'attribute')

    class Meta:
        model = Repository

    def __init__(self, *args, **kwargs):
        super(RepositoryForm, self).__init__(*args, **kwargs)
        try:
            self.fields['version'].initial = UserProfile.objects.get(
                pk=threadlocals.get_current_user().id
            ).version.id
        except UserProfile.DoesNotExist:
            pass


class RepositoryAdmin(AjaxSelectAdmin, MigasAdmin):
    form = RepositoryForm

    list_display = ('link', 'my_active', 'date', 'timeline',)
    list_select_related = ('schedule',)
    list_filter = ('active',)
    ordering = ('name',)
    search_fields = ('name', 'packages__name',)
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
            'classes': ('collapse',),
            'fields': ('attributes', 'excludes')
        }),
        (_('Schedule'), {
            'fields': ('date', 'schedule',)
        }),
    )

    def my_active(self, obj):
        return self.boolean_field(obj.active)

    my_active.allow_tags = True
    my_active.short_description = _('active')

    # QuerySet filter by user version
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
        is_new = (obj.pk is None)
        packages_after = form.cleaned_data['packages']
        super(RepositoryAdmin, self).save_model(request, obj, form, change)

        name_old = "%s" % form.initial.get('name')
        name_new = "%s" % obj.name

        # create physical repository when packages has been changed
        # or repository not have packages at first time
        # or name is changed (to avoid client errors)
        if ((is_new and len(packages_after) == 0)
                or compare_values(
                    obj.packages.values_list('id', flat=True),  # packages before
                    packages_after
                ) is False) or (name_new != name_old):
            create_physical_repository(request, obj, packages_after)

            # delete old repository by name changed
            if name_new != name_old and not is_new:
                remove_physical_repository(request, obj, name_old)

admin.site.register(Repository, RepositoryAdmin)


class ScheduleDelayline(admin.TabularInline):
    model = ScheduleDelay
    form = make_ajax_form(ScheduleDelay, {'attributes': 'attribute'})
    extra = 0
    ordering = ('delay',)


class ScheduleAdmin(MigasAdmin):
    list_display = ('link', 'description',)
    inlines = [ScheduleDelayline, ]
    extra = 0

admin.site.register(Schedule, ScheduleAdmin)


class PackageAdmin(MigasAdmin):
    list_display = ('link', 'store',)
    list_filter = ('store',)
    list_per_page = 25
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
