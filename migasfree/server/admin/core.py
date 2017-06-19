# -*- coding: utf-8 -*-

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin

from .migasfree import MigasAdmin, MigasFields

from ..models import (
    Attribute, AttributeSet, Checking, ClientProperty, ClientAttribute,
    Notification, Package, Platform, Pms, Property, Query, Deployment, Schedule,
    ScheduleDelay, Store, ServerAttribute, ServerProperty, UserProfile, Project,
    Policy, PolicyGroup,
)

from ..forms import (
    PropertyForm, DeploymentForm, ServerAttributeForm, StoreForm, PackageForm
)

from ..filters import ClientAttributeFilter, ServerAttributeFilter
from ..utils import compare_list_values
from ..tasks import (
    create_repository_metadata,
    remove_repository_metadata
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
        model=AttributeSet, name="included_attributes", description=_('included attributes')
    )
    excluded_attributes_link = MigasFields.objects_link(
        model=AttributeSet, name='excluded_attributes', description=_('excluded attributes')
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
    list_display = ('name', 'my_enabled')
    list_display_links = ('name',)
    list_filter = ('enabled',)
    search_fields = ('name',)

    my_enabled = MigasFields.boolean(model=Checking, name='enabled')


@admin.register(Attribute)
class AttributeAdmin(MigasAdmin):
    list_display = (
        'value_link', 'description', 'total_computers', 'property_link'
    )
    list_select_related = ('property_att',)
    list_filter = (ClientAttributeFilter,)
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


@admin.register(ClientAttribute)
class ClientAttributeAdmin(MigasAdmin):
    list_display = (
        'value_link', 'description', 'total_computers', 'property_link'
    )
    list_select_related = ('property_att',)
    list_filter = (ClientAttributeFilter,)
    fields = ('property_link', 'value', 'description')
    ordering = ('property_att', 'value')
    search_fields = ('value', 'description')
    readonly_fields = ('property_link', 'value')

    value_link = MigasFields.link(model=ClientAttribute, name='value')
    property_link = MigasFields.link(
        model=ClientAttribute,
        name='property_att',
        order='property_att__name'
    )

    def get_queryset(self, request):
        return super(ClientAttributeAdmin, self).get_queryset(request).extra(
            select={'total_computers': Attribute.TOTAL_COMPUTER_QUERY}
        )

    def has_add_permission(self, request):
        return False


@admin.register(Package)
class PackageAdmin(MigasAdmin):
    form = PackageForm
    list_display = (
        'name_link', 'project_link', 'store_link', 'deployments_link'
    )
    list_filter = ('project', 'store', 'deployment')
    list_select_related = ('project', 'store')
    search_fields = ('name', 'store__name')
    ordering = ('name',)

    name_link = MigasFields.link(model=Package, name='name')
    project_link = MigasFields.link(
        model=Package, name='project', order='project__name'
    )
    store_link = MigasFields.link(
        model=Package, name='store', order='store__name'
    )
    deployments_link = MigasFields.objects_link(
        model=Package, name='deployment_set'
    )

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == '++':
            # Packages filter by user project
            kwargs['queryset'] = Store.objects.filter(
                project__id=request.user.userprofile.project_id
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
        form.current_user = request.user
        return form

    def get_queryset(self, request):
        return super(PackageAdmin, self).get_queryset(
            request
            ).prefetch_related(
                'deployment_set'
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


@admin.register(ClientProperty)
class ClientPropertyAdmin(MigasAdmin):
    list_display = ('name_link', 'my_enabled', 'kind', 'my_auto_add')
    list_filter = ('enabled', 'kind', 'auto_add')
    ordering = ('name',)
    search_fields = ('name', 'prefix')
    form = PropertyForm
    fields = (
        'prefix', 'name', 'enabled',
        'language', 'code', 'kind', 'auto_add',
    )
    actions = None

    name_link = MigasFields.link(model=ClientProperty, name='name')
    my_enabled = MigasFields.boolean(model=ClientProperty, name='enabled')
    my_auto_add = MigasFields.boolean(model=ClientProperty, name='auto_add')


@admin.register(Property)
class PropertyAdmin(ClientPropertyAdmin):
    list_display = ('name_link', 'my_enabled', 'kind', 'my_auto_add', 'sort')
    fields = (
        'prefix', 'name', 'enabled',
        'language', 'code', 'kind', 'auto_add', 'sort'
    )
    search_fields = ('name',)


@admin.register(ServerProperty)
class ServerPropertyAdmin(MigasAdmin):
    list_display = ('name_link', 'prefix', 'my_enabled')
    fields = ('prefix', 'name', 'kind', 'enabled')
    search_fields = ('name', 'prefix')
    list_filter = ('enabled',)

    name_link = MigasFields.link(model=ServerProperty, name='name')
    my_enabled = MigasFields.boolean(model=ServerProperty, name='enabled')


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


@admin.register(Deployment)
class DeploymentAdmin(AjaxSelectAdmin, MigasAdmin):
    form = DeploymentForm
    list_display = (
        'name_link', 'project_link', 'my_enabled', 'start_date', 'schedule_link', 'timeline'
    )
    list_filter = ('enabled', 'project', 'schedule')
    search_fields = ('name', 'available_packages__name')
    list_select_related = ("project",)
    actions = ['regenerate_metadata']
    readonly_fields = ('timeline',)

    fieldsets = (
        (_('General'), {
            'fields': ('name', 'project', 'enabled', 'comment',)
        }),
        (_('Packages'), {
            'classes': ('collapse',),
            'fields': (
                'available_packages',
                'packages_to_install',
                'packages_to_remove',
            )
        }),
        (_('Default'), {
            'classes': ('collapse',),
            'fields': (
                'default_preincluded_packages',
                'default_included_packages',
                'default_excluded_packages',
            )
        }),
        (_('Attributes'), {
            'fields': ('included_attributes', 'excluded_attributes')
        }),
        (_('Schedule'), {
            'fields': ('start_date', 'schedule', 'timeline')
        }),
    )

    name_link = MigasFields.link(model=Deployment, name='name')
    project_link = MigasFields.link(
        model=Deployment, name='project', order='project__name'
    )
    schedule_link = MigasFields.link(
        model=Deployment, name='schedule', order='schedule__name'
    )
    my_enabled = MigasFields.boolean(model=Deployment, name='enabled')
    timeline = MigasFields.timeline()

    def regenerate_metadata(self, request, objects):
        if not self.has_change_permission(request):
            raise PermissionDenied

        for deploy in objects:
            create_repository_metadata(deploy, request=request)

    regenerate_metadata.short_description = _("Regenerate metadata")

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'available_packages':
            # Packages filter by user project
            kwargs['queryset'] = Package.objects.filter(
                project__id=request.user.userprofile.project_id
            )

            return db_field.formfield(**kwargs)

        if db_field.name == 'included_attributes':
            kwargs['queryset'] = Attribute.objects.filter(
                property_att__enabled=True
            )

            return db_field.formfield(**kwargs)

        return super(DeploymentAdmin, self).formfield_for_manytomany(
            db_field,
            request,
            **kwargs
        )

    def save_model(self, request, obj, form, change):
        is_new = (obj.pk is None)
        packages_after = list(
            map(int, form.cleaned_data.get('available_packages'))
        )
        super(DeploymentAdmin, self).save_model(request, obj, form, change)

        name_old = form.initial.get('name')
        name_new = obj.name

        # create physical repository when packages have been changed
        # or repository does not have packages at first time
        # or name has been changed (to avoid client errors)
        if ((is_new and len(packages_after) == 0)
                or compare_list_values(
                    obj.available_packages.values_list('id', flat=True),  # pkgs before
                    packages_after
                ) is False) or (name_new != name_old):
            create_repository_metadata(obj, packages_after, request)

            # delete old repository by name changed
            if name_new != name_old and not is_new:
                remove_repository_metadata(request, obj, name_old)

        Notification.objects.create(
            _('Deployment [%s] modified by user [%s] '
                '(<a href="%s">review changes</a>)') % (
                '<a href="{}">{}</a>'.format(
                    reverse('admin:server_deployment_change', args=(obj.id,)),
                    obj.name
                ),
                request.user,
                reverse('admin:server_deployment_history', args=(obj.id,))
            )
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super(DeploymentAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user

        return form

    def get_queryset(self, request):
        return super(DeploymentAdmin, self).get_queryset(
            request
        ).extra(
            select={
                'schedule_begin': '(SELECT delay FROM server_scheduledelay '
                                  'WHERE server_deployment.schedule_id = server_scheduledelay.schedule_id '
                                  'ORDER BY server_scheduledelay.delay LIMIT 1)',
                'schedule_end': '(SELECT delay+duration FROM server_scheduledelay '
                                'WHERE server_deployment.schedule_id = server_scheduledelay.schedule_id '
                                'ORDER BY server_scheduledelay.delay DESC LIMIT 1)'
            }
        ).select_related("project", "schedule")


class ScheduleDelayLine(admin.TabularInline):
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
    inlines = [ScheduleDelayLine]
    extra = 0

    name_link = MigasFields.link(model=Schedule, name='name')


@admin.register(Store)
class StoreAdmin(MigasAdmin):
    form = StoreForm
    list_display = ('name_link', 'project_link')
    search_fields = ('name',)
    list_filter = ('project',)
    ordering = ('name',)

    name_link = MigasFields.link(model=Store, name='name')
    project_link = MigasFields.link(
        model=Store, name='project', order='project__name'
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(StoreAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def get_queryset(self, request):
        return super(StoreAdmin, self).get_queryset(
            request
        ).select_related("project")


@admin.register(ServerAttribute)
class ServerAttributeAdmin(MigasAdmin):
    form = ServerAttributeForm
    list_display = (
        'value_link', 'description', 'total_computers', 'property_link'
    )
    list_select_related = ('property_att',)
    fields = ('property_att', 'value', 'description', 'computers')
    list_filter = (ServerAttributeFilter,)
    ordering = ('property_att', 'value',)
    search_fields = ('value', 'description')

    property_link = MigasFields.link(
        model=ServerAttribute, name='property_att', order='property_att__name'
    )
    value_link = MigasFields.link(model=ServerAttribute, name='value')

    def get_queryset(self, request):
        return super(ServerAttributeAdmin, self).get_queryset(request).extra(
            select={'total_computers': Attribute.TOTAL_COMPUTER_QUERY}
        )


@admin.register(UserProfile)
class UserProfileAdmin(MigasAdmin):
    list_display = ('name_link', 'first_name', 'last_name')
    list_filter = ('project',)
    ordering = ('username',)
    search_fields = ('username', 'first_name', 'last_name')

    name_link = MigasFields.link(model=UserProfile, name='username')


@admin.register(Project)
class ProjectAdmin(MigasAdmin):
    list_display = (
        'name_link',
        'platform_link',
        'pms_link',
        'my_auto_register_computers'
    )
    fields = ('name', 'platform', 'pms', 'auto_register_computers')
    list_filter = ('platform', 'pms')
    list_select_related = ('platform', 'pms')
    search_fields = ('name',)
    actions = None

    name_link = MigasFields.link(model=Project, name='name')
    platform_link = MigasFields.link(
        model=Project, name='platform', order='platform__name'
    )
    pms_link = MigasFields.link(model=Project, name='pms', order='pms__name')
    my_auto_register_computers = MigasFields.boolean(
        model=Project, name='auto_register_computers'
    )


@admin.register(PolicyGroup)
class PolicyGroupAdmin(MigasAdmin):
    form = make_ajax_form(
        PolicyGroup,
        {
            'included_attributes': 'attribute',
            'excluded_attributes': 'attribute'
        }
    )

    list_display = (
        'id', 'policy_link', 'priority',
        'included_attributes_link', 'excluded_attributes_link'
    )
    list_display_links = ('id',)
    list_filter = ('policy__name',)
    search_fields = (
        'policy__name', 'included_attributes__value',
        'excluded_attributes__value'
    )

    policy_link = MigasFields.link(model=PolicyGroup, name='policy')
    included_attributes_link = MigasFields.objects_link(
        model=PolicyGroup, name='included_attributes',
        description=_('included attributes')
    )
    excluded_attributes_link = MigasFields.objects_link(
        model=PolicyGroup, name='excluded_attributes',
        description=_('excluded attributes')
    )

    def get_queryset(self, request):
        return super(PolicyGroupAdmin, self).get_queryset(
            request
            ).prefetch_related(
                'included_attributes',
                'included_attributes__property_att',
                'excluded_attributes',
                'excluded_attributes__property_att'
            )


class PolicyGroupLine(admin.TabularInline):
    form = make_ajax_form(
        PolicyGroup,
        {
            'included_attributes': 'attribute',
            'excluded_attributes': 'attribute'
        }
    )
    form.declared_fields['included_attributes'].label = _('included attributes')
    form.declared_fields['excluded_attributes'].label = _('excluded attributes')

    model = PolicyGroup
    fields = (
        'priority', 'included_attributes',
        'excluded_attributes', 'packages_to_install'
    )
    ordering = ('priority',)
    extra = 0


@admin.register(Policy)
class PolicyAdmin(MigasAdmin):
    form = make_ajax_form(
        Policy,
        {
            'included_attributes': 'attribute',
            'excluded_attributes': 'attribute'
        }
    )
    form.declared_fields['included_attributes'].label = _('included attributes')
    form.declared_fields['excluded_attributes'].label = _('excluded attributes')

    list_display = (
        'name_link', 'included_attributes_link', 'excluded_attributes_link'
    )
    list_filter = ('enabled',)
    list_display_links = ('name_link',)
    search_fields = (
        'name', 'included_attributes__value', 'excluded_attributes__value'
    )
    fieldsets = (
        (_('General'), {
            'fields': (
                'name',
                'comment',
                'enabled',
            )
        }),
        (_('Application Area'), {
            'fields': (
                'included_attributes',
                'excluded_attributes',
            )
        }),
    )
    inlines = [PolicyGroupLine]
    extra = 0

    name_link = MigasFields.link(model=Policy, name='name')
    included_attributes_link = MigasFields.objects_link(
        model=Policy, name='included_attributes',
        description=_('included attributes')
    )
    excluded_attributes_link = MigasFields.objects_link(
        model=Policy, name='excluded_attributes',
        description=_('excluded attributes'),
    )
