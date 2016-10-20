# -*- coding: utf-8 -*-

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin

from .migasfree import MigasAdmin

from ..models import (
    Attribute, AttributeSet, Checking, ClientProperty, Feature, MessageServer,
    Notification, Package, Platform, Pms, Property, Query, Repository, Schedule,
    ScheduleDelay, Store, Tag, TagType, UserProfile, Version
)
from ..forms import PropertyForm, RepositoryForm, TagForm
from ..filters import FeatureFilter, TagFilter
from ..functions import compare_list_values
from ..tasks import (
    create_physical_repository,
    remove_physical_repository
)

admin.site.register(Attribute)


@admin.register(AttributeSet)
class AttributeSetAdmin(MigasAdmin):
    form = make_ajax_form(
        AttributeSet,
        {'attributes': 'attribute', 'excludes': 'attribute'}
    )
    list_display = ('name',)
    list_display_links = ('name',)


@admin.register(Checking)
class CheckingAdmin(MigasAdmin):
    list_display = ('name', 'my_active', 'my_alert')
    list_display_links = ('name',)
    list_filter = ('active',)

    def my_active(self, obj):
        return self.boolean_field(obj.active)

    my_active.allow_tags = True
    my_active.short_description = _('active')

    def my_alert(self, obj):
        return self.boolean_field(obj.alert)

    my_alert.allow_tags = True
    my_alert.short_description = _('alert')


@admin.register(ClientProperty)
class ClientPropertyAdmin(MigasAdmin):
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

    def my_link(self, obj):
        return obj.link()

    my_link.short_description = _("Property")

    def my_active(self, obj):
        return self.boolean_field(obj.active)

    my_active.allow_tags = True
    my_active.short_description = _('active')

    def my_auto(self, obj):
        return self.boolean_field(obj.auto)

    my_auto.allow_tags = True
    my_auto.short_description = _('auto')


@admin.register(Feature)
class FeatureAdmin(MigasAdmin):
    list_display = (
        'my_link', 'description', 'total_computers', 'property_att'
    )
    list_select_related = ('property_att',)
    list_filter = (FeatureFilter,)
    fields = ('property_att', 'value', 'description')
    ordering = ('property_att', 'value')
    search_fields = ('value', 'description')
    readonly_fields = ('property_att', 'value')

    def my_link(self, obj):
        return obj.link()

    my_link.short_description = _("Attribute")

    def get_queryset(self, request):
        return super(FeatureAdmin, self).get_queryset(request).extra(
            select={'total_computers': Attribute.TOTAL_COMPUTER_QUERY}
        )

    def has_add_permission(self, request):
        return False


@admin.register(MessageServer)
class MessageServerAdmin(MigasAdmin):
    list_display = ('id', 'date', 'text')
    list_display_links = ('id',)
    ordering = ('-date',)
    list_filter = ('date',)
    search_fields = ('text', 'date')
    readonly_fields = ('text', 'date')


@admin.register(Package)
class PackageAdmin(MigasAdmin):
    list_display = ('my_link', 'store', 'repos_link')
    list_filter = ('version', 'store', 'repository')
    list_per_page = 25
    list_select_related = ('version',)
    search_fields = ('name', 'store__name')
    ordering = ('name',)

    def my_link(self, obj):
        return obj.link()

    my_link.short_description = _("Package/Set")

    def get_form(self, request, obj=None, **kwargs):
        form = super(PackageAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['version'].widget.can_add_related = False
        form.base_fields['store'].widget.can_add_related = False

        return form


@admin.register(Platform)
class PlatformAdmin(MigasAdmin):
    list_display = ('my_link',)

    actions = ['delete_selected']

    def my_link(self, obj):
        return obj.link()

    my_link.short_description = _("Platform")

    def delete_selected(self, request, objects):
        if not self.has_delete_permission(request):
            raise PermissionDenied

        return render(
            request,
            'platform_confirm_delete_selected.html',
            {
                'object_list': ', '.join([x.__str__() for x in objects])
            }
        )

    delete_selected.short_description = _("Delete selected "
        "%(verbose_name_plural)s")


@admin.register(Pms)
class PmsAdmin(MigasAdmin):
    list_display = ('my_link',)

    def my_link(self, obj):
        return obj.link()

    my_link.short_description = _("Package Management System")


@admin.register(Property)
class PropertyAdmin(ClientPropertyAdmin):
    list_display = ('my_link', 'my_active', 'kind', 'my_auto', 'my_tag')
    fields = (
        'prefix', 'name', 'active',
        'language', 'code', 'kind', 'auto', 'tag'
    )

    def my_tag(self, obj):
        return self.boolean_field(obj.tag)

    my_tag.allow_tags = True
    my_tag.short_description = _('tag')


@admin.register(Query)
class QueryAdmin(MigasAdmin):
    list_display = ('name', 'description')
    list_display_links = ('name',)
    actions = ['run_query']

    def run_query(self, request, queryset):
        for query in queryset:
            return redirect(reverse('query', args=(query.id,)))

    run_query.short_description = _("Run Query")


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

    def my_link(self, obj):
        return obj.link()

    my_link.short_description = _("Repository")

    def my_active(self, obj):
        return self.boolean_field(obj.active)

    my_active.allow_tags = True
    my_active.short_description = _('active')

    def get_queryset(self, request):
        return self.model._default_manager.by_version(
            request.user.userprofile.version_id
        )

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'packages':
            # Packages filter by user version
            kwargs['queryset'] = Package.objects.filter(
                version__id=request.user.userprofile.version_id
            )

            return db_field.formfield(**kwargs)

        if db_field.name == 'attributes':
            kwargs['queryset'] = Attribute.objects.filter(
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
        packages_after = list(map(int, form.cleaned_data.get('packages')))
        super(RepositoryAdmin, self).save_model(request, obj, form, change)

        name_old = form.initial.get('name')
        name_new = obj.name

        # create physical repository when packages has been changed
        # or repository not have packages at first time
        # or name is changed (to avoid client errors)
        if ((is_new and len(packages_after) == 0)
                or compare_list_values(
                    obj.packages.values_list('id', flat=True),  # pkgs before
                    packages_after
                ) is False) or (name_new != name_old):
            create_physical_repository(request, obj, packages_after)

            # delete old repository by name changed
            if name_new != name_old and not is_new:
                remove_physical_repository(request, obj, name_old)

        Notification.objects.create(
            _('Repository [%s] modified by user [%s] '
                '(<a href="%s">review changes</a>)') % (
                obj.name,
                request.user,
                reverse('admin:server_repository_history', args=(obj.id,))
            )
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super(RepositoryAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['version'].widget.can_add_related = False
        form.base_fields['schedule'].widget.can_add_related = False
        form.current_user = request.user

        return form


class ScheduleDelayline(admin.TabularInline):
    model = ScheduleDelay
    fields = ('delay', 'attributes', 'total_computers', 'duration')
    form = make_ajax_form(ScheduleDelay, {'attributes': 'attribute_computers'})
    ordering = ('delay',)
    readonly_fields = ('total_computers',)
    extra = 0


@admin.register(Schedule)
class ScheduleAdmin(MigasAdmin):
    list_display = ('my_link', 'description')
    inlines = [ScheduleDelayline]
    extra = 0

    def my_link(self, obj):
        return obj.link()

    my_link.short_description = _("Schedule")


@admin.register(Store)
class StoreAdmin(MigasAdmin):
    list_display = ('my_link',)
    search_fields = ('name',)

    def my_link(self, obj):
        return obj.link()

    my_link.short_description = _("Store")

    def get_queryset(self, request):
        return self.model._default_manager.by_version(
            request.user.userprofile.version_id
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super(StoreAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['version'].widget.can_add_related = False

        return form


@admin.register(TagType)
class TagTypeAdmin(MigasAdmin):
    list_display = ('my_link', 'prefix', 'my_active')
    fields = ('prefix', 'name', 'kind', 'active')

    def my_link(self, obj):
        return obj.link()

    my_link.short_description = _("Tag Type")

    def my_active(self, obj):
        return self.boolean_field(obj.active)

    my_active.allow_tags = True
    my_active.short_description = _('active')


@admin.register(Tag)
class TagAdmin(MigasAdmin):
    form = TagForm
    list_display = ('my_link', 'description', 'total_computers', 'property_att')
    fields = ('property_att', 'value', 'description', 'computers')
    list_filter = (TagFilter,)
    ordering = ('property_att', 'value',)
    search_fields = ('value', 'description')

    def my_link(self, obj):
        return obj.link()

    my_link.short_description = _("Tag")

    def get_queryset(self, request):
        return super(TagAdmin, self).get_queryset(request).extra(
            select={'total_computers': Attribute.TOTAL_COMPUTER_QUERY}
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super(TagAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['property_att'].widget.can_add_related = False

        return form


@admin.register(UserProfile)
class UserProfileAdmin(MigasAdmin):
    list_display = ('my_link',)
    ordering = ('username',)

    def my_link(self, obj):
        return obj.link()

    my_link.short_description = _("User Profile")

    def get_form(self, request, obj=None, **kwargs):
        form = super(UserProfileAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['version'].widget.can_add_related = False
        form.base_fields['groups'].widget.can_add_related = False

        return form


@admin.register(Version)
class VersionAdmin(MigasAdmin):
    list_display = (
        'my_link',
        'platform',
        'pms',
        'computerbase',
        'my_autoregister'
    )
    fields = ('name', 'platform', 'pms', 'computerbase', 'autoregister', 'base')
    actions = None

    def my_link(self, obj):
        return obj.link()

    my_link.short_description = _("Version")

    def my_autoregister(self, obj):
        return self.boolean_field(obj.autoregister)

    my_autoregister.allow_tags = True
    my_autoregister.short_description = _('autoregister')

    def get_form(self, request, obj=None, **kwargs):
        form = super(VersionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['pms'].widget.can_add_related = False
        form.base_fields['platform'].widget.can_add_related = False

        return form
