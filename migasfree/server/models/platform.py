# -*- coding: utf-8 *-*

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import MigasLink


class PlatformManager(models.Manager):
    def create(self, name):
        plat = Platform()
        plat.name = name
        plat.save()

        return plat


class Platform(models.Model, MigasLink):
    """
    Computer Platform
    """

    name = models.CharField(
        verbose_name=_("name"),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    objects = PlatformManager()

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Platform")
        verbose_name_plural = _("Platforms")
        permissions = (("can_save_platform", "Can save Platform"),)
