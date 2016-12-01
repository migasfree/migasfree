# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models

from .models import Application
from form_utils.widgets import ImageWidget

from migasfree.server.admin.migasfree import MigasAdmin, MigasFields


@admin.register(Application)
class ApplicationAdmin(MigasAdmin):
    formfield_overrides = {
        models.ImageField: {'widget': ImageWidget}
    }
    list_display = ('name', 'version_link', 'score', 'level', 'category',)
    list_display_links = ('name',)
    list_filter = ('version', 'level', 'category')
    ordering = ('name',)
    fields = (
        'name', 'version', 'category', 'level', 'score', 'icon',
        'description', 'packages_to_install'
    )

    version_link = MigasFields.link(
        model=Application, name='version', order='version__name'
    )

    def __str__(self):
        return self.name

    class Media:
        css = {
            "screen, projection, handheld": ("css/star-rating.min.css",)
        }
        js = ("js/star-rating.min.js", "js/app.js")
