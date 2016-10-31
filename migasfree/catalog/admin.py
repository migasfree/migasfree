# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .models import Application
from form_utils.widgets import ImageWidget

from migasfree.server.admin.migasfree import MigasAdmin


@admin.register(Application)
class ApplicationAdmin(MigasAdmin):
    formfield_overrides = {
        models.ImageField: {'widget': ImageWidget}
    }
    list_display = ('my_link', 'version', 'score', 'level', 'category',)
    list_filter = ('version', 'level', 'category')
    ordering = ('name',)
    fields = (
        'name', 'version', 'category', 'level', 'score', 'icon',
        'description', 'packages_to_install'
    )

    def my_link(self, obj):
        return obj.link()
    my_link.short_description = _("Application")

    def __str__(self):
        return self.name

    class Media:
        css = {
            "screen, projection, handheld": ("css/star-rating.min.css",)
        }
        js = ("js/star-rating.min.js", "js/app.js")
