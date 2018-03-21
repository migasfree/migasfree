# -*- coding: utf-8 *-*

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import MigasLink


class DomainPlatformManager(models.Manager):
    def scope(self, user):
        qs = super(DomainPlatformManager, self).get_queryset()
        if not user.is_view_all():
            qs = qs.filter(project__in=user.get_projects()).distinct()
        return qs


class PlatformManager(DomainPlatformManager):
    def create(self, name):
        obj = Platform()
        obj.name = name
        obj.save()

        return obj


@python_2_unicode_compatible
class Platform(models.Model, MigasLink):
    """
    Computer Platform
    """

    name = models.CharField(
        verbose_name=_("name"),
        max_length=50,
        unique=True
    )

    objects = PlatformManager()

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Platform")
        verbose_name_plural = _("Platforms")
        permissions = (("can_save_platform", "Can save Platform"),)
