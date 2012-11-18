# -*- coding: utf-8 -*-

import os

from django.db import models
from django.utils.translation import ugettext_lazy as _

from server.models.pms import Pms
from common import link, PLATFORM_CHOICES
from migasfree.settings import MIGASFREE_REPO_DIR


class Version(models.Model):
    """
    Version of S.O. by example 'Ubuntu natty 32bit' or 'AZLinux-2'
    This is 'your distribution', a set of computers with a determinate
    Distribution for personalize.
    """
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        unique=True
    )

    pms = models.ForeignKey(
        Pms,
        verbose_name=unicode(_("package management system"))
    )

    computerbase = models.CharField(
        unicode(_("Actual line computer")),
        max_length=50,
        help_text=unicode(_("Computer with the actual line software")),
        default="---"
    )

    base = models.TextField(
        unicode(_("Actual line packages")),
        null=False,
        blank=True,
        help_text=unicode(_("List ordered of packages of actual line computer"))
    )

    autoregister = models.BooleanField(
        unicode(_("autoregister")),
        default=False,
        help_text="Is not neccesary a user for register the computer in database and get the keys."
    )

    platform = models.IntegerField(
        unicode(_("platform")),
        default=0,
        choices=PLATFORM_CHOICES
    )

    def __unicode__(self):
        return self.name

    def create_dirs(self):
        _repos = os.path.join(MIGASFREE_REPO_DIR, self.name, 'REPOSITORIES')
        if not os.path.exists(_repos):
            os.makedirs(_repos)

        _stores = os.path.join(MIGASFREE_REPO_DIR, self.name, 'STORES')
        if not os.path.exists(_stores):
            os.makedirs(_stores)

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "-")
        self.create_dirs()
        self.base = self.base.replace("\r\n", "\n")
        super(Version, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # remove the directory of this version
        os.system("rm -rf %s" % os.path.join(MIGASFREE_REPO_DIR, self.name))
        super(Version, self).delete(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Version"))
        verbose_name_plural = unicode(_("Versions"))
        permissions = (("can_save_version", "Can save Version"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
