# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from common import link


class Schedule(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    description = models.TextField(
        unicode(_("description")),
        null=True,
        blank=True
    )

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Schedule"))
        verbose_name_plural = unicode(_("Schedules"))
        permissions = (("can_save_schedule", "Can save Schedule"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
