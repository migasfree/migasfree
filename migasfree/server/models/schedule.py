# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import MigasLink


@python_2_unicode_compatible
class Schedule(models.Model, MigasLink):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=50,
        null=False,
        blank=False,
        default='default',
        unique=True
    )

    description = models.TextField(
        verbose_name=_("description"),
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")
        permissions = (("can_save_schedule", "Can save Schedule"),)
