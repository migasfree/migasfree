# -*- coding: utf-8 -*-

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin

from .migasfree import MigasAdmin, MigasFields

from ..models import (
    Attribute, AttributeSet, Checking, ClientProperty, Feature, MessageServer,
    Notification, Package, Platform, Pms, Property, Query, Repository, Schedule,
    ScheduleDelay, Store, Tag, TagType, UserProfile, Version
)

from ..forms import (
    PropertyForm, RepositoryForm, TagForm, StoreForm, PackageForm
)

from ..filters import FeatureFilter, TagFilter
from ..functions import compare_list_values
from ..tasks import (
    create_physical_repository,
    remove_physical_repository
)


@admin.register(AttributeSet)
class AttributeSetAdmin(MigasAdmin):
    form = make_ajax_form(
        AttributeSet,
        {
            'included_attributes': 'attribute',
            'excluded_attributes': 'attribute',
        }
    )
    list_display = ('name_link', 'included_attributes_link', 'excluded_attributes_link')
    list_filter = ('enabled',)
    list_display_links = ('name_link',)
    search_fields = ('name', 'included_attributes__value', 'excluded_attributes__value')

    name_link = MigasFields.link(model=AttributeSet, name='name')
    included_attributes_link = MigasFields.objects_link(
        model=AttributeSet, name="included_attributes"
    )
    excluded_attributes_link = MigasFields.objects_link(
        model=AttributeSet, name='excluded_attributes'
    )

    def get_queryset(self, request):
        return super(AttributeSetAdmin, self).get_queryset(
            request
        ).prefetch_related(
            'included_attributes',
            'included_attributes__property_att',
            'excluded_attributes',
            'excluded_attributes__property_att'
        )


@admin.register(Checking)
class CheckingAdmin(MigasAdmin):
    list_display = ('name', 'my_active')
    list_display_links = ('name',)
    list_filter = ('active',)
    search_fields = ('name',)

    my_active = MigasFields.boolean(model=Checking, name='active')


@admin.register(ClientProperty)
class ClientPropertyAdmin(MigasAdmin):
    list_display = ('name_link', 'my_active', 'kind', 'my_auto')
    list_filter = ('active', 'kind', 'auto')
    ordering = ('name',)
    search_fields = ('name', 'prefix')
    form = PropertyForm
    fields = (
        'prefix', 'name', 'active',
        'language', 'code', 'kind', 'auto',
    )
    actions = None

    name_link = MigasFields.link(model=ClientProperty, name='name')
    my_active = MigasFields.boolean(model=ClientProperty, name='active')
    my_auto = MigasFields.boolean(model=ClientProperty, name='auto')


@admin.register(Attribute)
class AttributeAdmin(MigasAdmin):
    list_display = (
        'value_link', 'description', 'total_computers', 'property_link'
    )
    list_select_related = ('property_att',)
    list_filter = (FeatureFilter,)
    fields = ('property_link', 'value', 'description')
    ordering = ('property_att', 'value')
    search_fields = ('value', 'description')
    readonly_fields = ('property_link', 'value')

    value_link = MigasFields.link(model=Attribute, name='value')
    property_link = MigasFields.link(
        model=Attribute,
        name='property_att',
        order='property_att__name'
    )

    def get_queryset(self, request):
        return super(AttributeAdmin, self).get_queryset(request).extra(
            select={'total_computers': Attribute.TOTAL_COMPUTER_QUERY}
        )

    def has_add_permission(self, request):
        return False


@admin.register(Feature)
class FeatureAdmin(MigasAdmin):
    list_display = (
        'value_link', 'description', 'total_computers', 'property_link'
    )
    list_select_related = ('property_att',)
    list_filter = (FeatureFilter,)
    fields = ('property_link', 'value', 'description')
    ordering = ('property_att', 'value')
    search_fields = ('value', 'description')
    readonly_fields = ('property_link', 'value')

    value_link = MigasFields.link(model=Feature, name='value')
    property_link = MigasFields.link(
        model=Feature,
        name='property_att',
        order='property_att__name'
    )

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
    form = PackageForm
    list_display = (
        'name_link', 'version_link', 'store_link', 'repositories_link'
    )
    list_filter = ('version', 'store', 'repository')
    list_select_related = ('version', 'store')
    search_fields = ('name', 'store__name')
    ordering = ('name',)

    name_link = MigasFields.link(model=Package, name='name')
    version_link = MigasFields.link(
        model=Package, name='version', order="version__name"
    )
    store_link = MigasFields.link(
        model=Package, name='store', order="store__name"
    )
    repositories_link = MigasFields.objects_link(
        model=Package, name='repository_set'
    )

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == '++':
            # Packages filter by user version
            kwargs['queryset'] = Store.objects.filter(
                version__id=request.user.userprofile.version_id
            )

            return db_field.formfield(**kwargs)

        return super(PackageAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

    class Media:
        js = ('js/package_admin.js',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(PackageAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['version'].widget.can_add_related = False
        form.base_fields['store'].widget.can_add_related = False
        form.current_user = request.user
        return form

    def get_queryset(self, request):
        return super(PackageAdmin, self).get_queryset(
            request
            ).prefetch_related(
                'repository_set'
            )


@admin.register(Platform)
class PlatformAdmin(MigasAdmin):
    list_display = ('name_link',)
    actions = ['delete_selected']
    search_fields = ('name',)

    name_link = MigasFields.link(model=Platform, name='name')

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
    list_display = ('name_link',)
    search_fields = ('name',)

    name_link = MigasFields.link(model=Pms, name='name')


@admin.register(Property)
class PropertyAdmin(ClientPropertyAdmin):
    list_display = ('name_link', 'my_active', 'kind', 'my_auto', 'my_tag')
    fields = (
        'prefix', 'name', 'active',
        'language', 'code', 'kind', 'auto', 'tag'
    )
    search_fields = ('name',)

    my_tag = MigasFields.boolean(model=Property, name='tag')


@admin.register(Query)
class QueryAdmin(MigasAdmin):
    list_display = ('name', 'description')
    list_display_links = ('name',)
    actions = ['run_query']
    search_fields = ('name', 'description')

    def run_query(self, request, queryset):
        for query in queryset:
            return redirect(reverse('query', args=(query.id,)))

    run_query.short_description = _("Run Query")


@admin.register(Repository)
class RepositoryAdmin(AjaxSelectAdmin, MigasAdmin):
    form = RepositoryForm
    list_display = (
        'name_link', 'version_link', 'my_active', 'date', 'schedule_link', 'timeline'
    )
    list_filter = ('active', 'version', 'schedule')
    search_fields = ('name', 'packages__name')
    list_select_related = ("version",)
    actions = ['regenerate_metadata']

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
        (_('Attributes'), {
            'fields': ('attributes', 'excludes')
        }),
        (_('Schedule'), {
            'fields': ('date', 'schedule',)
        }),
    )

    name_link = MigasFields.link(model=Repository, name='name')
    version_link = MigasFields.link(
        model=Repository, name='version', order="version__name"
    )
    schedule_link = MigasFields.link(
        model=Repository, name='schedule', order="schedule__name"
    )
    my_active = MigasFields.boolean(model=Repository, name='active')
    timeline = MigasFields.timeline(model=Repository)

    def regenerate_metadata(self, request, objects):
        if not self.has_change_permission(request):
            raise PermissionDenied

        for repo in objects:
            create_physical_repository(repo, request=request)

    regenerate_metadata.short_description = _("Regenerate metadata")

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

        # create physical repository when packages have been changed
        # or repository does not have packages at first time
        # or name has been changed (to avoid client errors)
        if ((is_new and len(packages_after) == 0)
                or compare_list_values(
                    obj.packages.values_list('id', flat=True),  # pkgs before
                    packages_after
                ) is False) or (name_new != name_old):
            create_physical_repository(obj, packages_after, request)

            # delete old repository by name changed
            if name_new != name_old and not is_new:
                remove_physical_repository(request, obj, name_old)

        Notification.objects.create(
            _('Repository [%s] modified by user [%s] '
                '(<a href="%s">review changes</a>)') % (
                '<a href="{}">{}</a>'.format(
                    reverse('admin:server_repository_change', args=(obj.id,)),
                    obj.name
                ),
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

    def get_queryset(self, request):
        return super(RepositoryAdmin, self).get_queryset(
            request
        ).extra(
            select={
                'schedule_begin': '(SELECT delay FROM server_scheduledelay '
                                  'WHERE server_repository.schedule_id = server_scheduledelay.schedule_id '
                                  'ORDER BY server_scheduledelay.delay LIMIT 1)',
                'schedule_end': '(SELECT delay+duration FROM server_scheduledelay '
                                'WHERE server_repository.schedule_id = server_scheduledelay.schedule_id '
                                'ORDER BY server_scheduledelay.delay DESC LIMIT 1)'
            }
        ).select_related("version", "schedule")


class ScheduleDelayline(admin.TabularInline):
    model = ScheduleDelay
    fields = ('delay', 'attributes', 'total_computers', 'duration')
    form = make_ajax_form(ScheduleDelay, {'attributes': 'attribute_computers'})
    ordering = ('delay',)
    readonly_fields = ('total_computers',)
    extra = 0


@admin.register(Schedule)
class ScheduleAdmin(MigasAdmin):
    list_display = ('name_link', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)
    inlines = [ScheduleDelayline]
    extra = 0

    name_link = MigasFields.link(model=Schedule, name='name')


@admin.register(Store)
class StoreAdmin(MigasAdmin):
    form = StoreForm
    list_display = ('name_link', 'version_link')
    search_fields = ('name',)
    list_filter = ('version',)
    ordering = ('name',)

    name_link = MigasFields.link(model=Store, name='name')
    version_link = MigasFields.link(
        model=Store, name='version', order='version__name'
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(StoreAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['version'].widget.can_add_related = False
        form.current_user = request.user
        return form

    def get_queryset(self, request):
        return super(StoreAdmin, self).get_queryset(
            request
        ).select_related("version")


@admin.register(TagType)
class TagTypeAdmin(MigasAdmin):
    list_display = ('name_link', 'prefix', 'my_active')
    fields = ('prefix', 'name', 'kind', 'active')
    search_fields = ('name', 'prefix')
    list_filter = ('active',)

    name_link = MigasFields.link(model=TagType, name='name')
    my_active = MigasFields.boolean(model=TagType, name='active')


@admin.register(Tag)
class TagAdmin(MigasAdmin):
    form = TagForm
    list_display = (
        'value_link', 'description', 'total_computers', 'property_link'
    )
    list_select_related = ('property_att',)
    fields = ('property_att', 'value', 'description', 'computers')
    list_filter = (TagFilter,)
    ordering = ('property_att', 'value',)
    search_fields = ('value', 'description')

    property_link = MigasFields.link(
        model=Tag, name='property_att', order='property_att__name'
    )
    value_link = MigasFields.link(model=Tag, name='value')

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
    list_display = ('name_link', 'first_name', 'last_name')
    list_filter = ('version',)
    ordering = ('username',)
    search_fields = ('username', 'first_name', 'last_name')

    name_link = MigasFields.link(model=UserProfile, name='username')

    def get_form(self, request, obj=None, **kwargs):
        form = super(UserProfileAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['version'].widget.can_add_related = False
        form.base_fields['groups'].widget.can_add_related = False

        return form


@admin.register(Version)
class VersionAdmin(MigasAdmin):
    list_display = (
        'name_link',
        'platform_link',
        'pms_link',
        'my_autoregister'
    )
    fields = ('name', 'platform', 'pms', 'computerbase', 'autoregister', 'base')
    list_filter = ('platform', 'pms')
    list_select_related = ('platform', 'pms')
    search_fields = ('name',)
    actions = None

    name_link = MigasFields.link(model=Version, name='name')
    platform_link = MigasFields.link(
        model=Version, name='platform', order='platform__name'
    )
    pms_link = MigasFields.link(model=Version, name='pms', order='pms__name')
    my_autoregister = MigasFields.boolean(model=Version, name='autoregister')

    def get_form(self, request, obj=None, **kwargs):
        form = super(VersionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['pms'].widget.can_add_related = False
        form.base_fields['platform'].widget.can_add_related = False

        return form
