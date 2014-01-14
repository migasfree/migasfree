# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from common import link


class Pms(models.Model):
    """
    Package Management System

    Each distribution of linux have a P.M.S. For example Fedora uses yum,
    Ubuntu uses apt, openSUSE zypper, etc.

    By default, migasfree is configured for work whith apt, yum and zypper.

    This model is used for say to migasfree server how must:
      - create the metadata of the repositories in the server.
      - define the source list file of repositories for the client.
      - get info of packages in the server for the view 'Packages Information'.
    """

    name = models.CharField(
        _("name"),
        max_length=50,
        unique=True
    )

    slug = models.CharField(
        _("slug"),
        max_length=50,
        null=True,
        blank=True,
        default="REPOSITORIES"
    )

    createrepo = models.TextField(
        _("create repository"),
        null=True,
        blank=True,
        help_text=_("Code bash. Define how create the metadata of repositories in the migasfree server.")
    )

    info = models.TextField(
        _("package information"),
        null=True,
        blank=True,
        help_text=_("Code bash. Define how get info of packages in the server")
    )

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.createrepo = self.createrepo.replace("\r\n", "\n")
        self.repository = self.repository.replace("\r\n", "\n")
        self.info = self.info.replace("\r\n", "\n")
        super(Pms, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Package Management System")
        verbose_name_plural = _("Package Management Systems")
        permissions = (("can_save_pms", "Can save Package Management System"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
