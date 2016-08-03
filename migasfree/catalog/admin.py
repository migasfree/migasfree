# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models

from .models import Application
from form_utils.widgets import ImageWidget


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ImageField: {'widget': ImageWidget}
    }
    list_display = ('name', 'version', 'score', 'level', 'category',)
    list_filter = ('version', 'level', 'category')
    ordering = ('name',)
    fields = (
        'name', 'version', 'category', 'level', 'score', 'icon',
        'description', 'packages_to_install'
    )

    class Media:
        css = {
            "screen, projection, handheld": ("css/star-rating.min.css",)
        }
        js = ("js/star-rating.min.js", "js/app.js")
