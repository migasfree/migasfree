# -*- coding: utf-8 -*-

import os
import shutil

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from migasfree.server.models import Pms, Platform, MigasLink


class Version(models.Model, MigasLink):
    """
    Version of S.O. by example 'Ubuntu natty 32bit' or 'AZLinux-2'
    This is 'your distribution', a set of computers with a determinate
    Distribution for personalize.
    """
    name = models.CharField(
        _("name"),
        max_length=50,
        unique=True
    )

    pms = models.ForeignKey(
        Pms,
        verbose_name=_("package management system")
    )

    computerbase = models.CharField(
        _("Actual line computer"),
        max_length=50,
        help_text=_("Computer with the actual line software"),
        default="---"
    )

    base = models.TextField(
        _("Actual line packages"),
        null=False,
        blank=True,
        help_text=_("List ordered of packages of actual line computer")
    )

    autoregister = models.BooleanField(
        _("autoregister"),
        default=False,
        help_text=_("Is not neccesary a user for register the computer in \
                     database and get the keys.")
    )

    platform = models.ForeignKey(
        Platform,
        verbose_name=_("platform")
    )

    def __unicode__(self):
        return self.name

    def create_dirs(self):
        _repos = os.path.join(
            settings.MIGASFREE_REPO_DIR,
            self.name,
            'REPOSITORIES'
        )
        if not os.path.exists(_repos):
            os.makedirs(_repos)

        _stores = os.path.join(settings.MIGASFREE_REPO_DIR, self.name, 'STORES')
        if not os.path.exists(_stores):
            os.makedirs(_stores)

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "-")
        self.create_dirs()
        self.base = self.base.replace("\r\n", "\n")
        super(Version, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # remove the directory of this version
        path = os.path.join(settings.MIGASFREE_REPO_DIR, self.name)
        if os.path.exists(path):
            shutil.rmtree(path)
        super(Version, self).delete(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Version")
        verbose_name_plural = _("Versions")
        permissions = (("can_save_version", "Can save Version"),)


def get_version_names():
    result = []
    for item in Version.objects.all().order_by("name"):
        result.append([item.id, item.name])

    return result
