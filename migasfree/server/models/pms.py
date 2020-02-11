# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import MigasLink


class Pms(models.Model, MigasLink):
    """
    Package Management System

    Each distribution of linux have a P.M.S. For example Fedora uses yum,
    Ubuntu uses apt, openSUSE zypper, etc.

    By default, migasfree is configured for work with apt, yum and zypper.

    This model is used for say to migasfree server how must:
      - create the metadata of the repositories in the server.
      - define the source list file of repositories for the client.
      - get info of packages in the server for the view 'Packages Information'.
    """

    name = models.CharField(
        verbose_name=_("name"),
        max_length=50,
        unique=True
    )

    slug = models.CharField(
        verbose_name=_("slug"),
        max_length=50,
        null=True,
        blank=True,
        default="REPOSITORIES"
    )

    createrepo = models.TextField(
        verbose_name=_("create repository"),
        null=True,
        blank=True,
        help_text=_("Bash code. Define how create the metadata of "
                    "repositories in the migasfree server.")
    )

    info = models.TextField(
        verbose_name=_("package information"),
        null=True,
        blank=True,
        help_text=_("Bash code. Define how get info of packages in the server")
    )

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.createrepo = self.createrepo.replace("\r\n", "\n")
        self.info = self.info.replace("\r\n", "\n")
        super(Pms, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        app_label = 'server'
        verbose_name = _("Package Management System")
        verbose_name_plural = _("Package Management Systems")
        permissions = (("can_save_pms", "Can save Package Management System"),)
