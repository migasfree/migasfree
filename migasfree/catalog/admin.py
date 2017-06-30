# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ajax_select import make_ajax_form
from form_utils.widgets import ImageWidget

from migasfree.server.admin.migasfree import MigasAdmin, MigasFields

from .models import Application, PackagesByProject


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


@admin.register(Application)
class ApplicationAdmin(MigasAdmin):
    formfield_overrides = {
        models.ImageField: {'widget': ImageWidget}
    }
    list_display = ('name_link', 'score', 'level', 'category',)
    list_filter = ('level', 'category')
    ordering = ('name',)
    fields = (
        'name', 'category', 'level',
        'score', 'icon', 'description'
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
