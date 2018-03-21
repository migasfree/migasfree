# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ajax_select import make_ajax_form

from migasfree.server.admin.migasfree import MigasAdmin, MigasFields

from .models import Application, PackagesByProject, Policy, PolicyGroup
from .forms import ApplicationForm, PolicyForm, PolicyGroupForm


@admin.register(PackagesByProject)
class PackagesByProjectAdmin(MigasAdmin):
    form = make_ajax_form(
        PackagesByProject,
        {'project': 'project'}
    )

    list_display = (
        'id', 'application_link', 'project_link', 'packages_to_install'
    )
    list_display_links = ('id',)
    list_filter = ('application__name',)
    search_fields = ('application__name', 'packages_to_install')

    application_link = MigasFields.link(model=PackagesByProject, name='application')
    project_link = MigasFields.objects_link(
        model=PackagesByProject, name='project',
        description=_('project')
    )

    def get_queryset(self, request):
        return super(PackagesByProjectAdmin, self).get_queryset(
            request
        ).prefetch_related('project')


class PackagesByProjectLine(admin.TabularInline):
    model = PackagesByProject
    fields = ('project', 'packages_to_install')
    ordering = ('project',)
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(PackagesByProjectLine, self).get_formset(request, obj, **kwargs)
        formset.form.base_fields['project'].widget.can_change_related = False
        formset.form.base_fields['project'].widget.can_add_related = False

        return formset

    def get_queryset(self, request):
        qs = super(PackagesByProjectLine, self).get_queryset(request)
        user = request.user.userprofile
        if not user.is_view_all():
            qs = qs.filter(project__in=user.get_projects())
        return qs


@admin.register(Application)
class ApplicationAdmin(MigasAdmin):
    form = ApplicationForm
    list_display = ('name_link', 'score', 'level', 'category',)
    list_filter = ('level', 'category')
    ordering = ('name',)
    fields = (
        'name', 'category', 'level',
        'score', 'icon', 'available_for_attributes', 'description'
    )
    search_fields = ('name', 'description')

    inlines = [PackagesByProjectLine]
    extra = 0

    name_link = MigasFields.link(model=Application, name="name")
    project_link = MigasFields.link(
        model=Application, name='project', order='project__name'
    )

    def __str__(self):
        return self.name

    class Media:
        css = {
            "screen, projection, handheld": ("css/star-rating.min.css",)
        }
        js = ("js/star-rating.min.js", "js/app.js")


@admin.register(PolicyGroup)
class PolicyGroupAdmin(MigasAdmin):
    form = PolicyGroupForm
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
    form = PolicyGroupForm
    model = PolicyGroup
    fields = (
        'priority', 'included_attributes',
        'excluded_attributes', 'applications'
    )
    ordering = ('priority',)
    extra = 0


@admin.register(Policy)
class PolicyAdmin(MigasAdmin):
    form = PolicyForm
    list_display = (
        'name_link', 'my_enabled', 'my_exclusive',
        'included_attributes_link', 'excluded_attributes_link'
    )
    list_filter = ('enabled', 'exclusive')
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
                'exclusive',
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
    my_enabled = MigasFields.boolean(model=Policy, name='enabled')
    my_exclusive = MigasFields.boolean(model=Policy, name='exclusive')
