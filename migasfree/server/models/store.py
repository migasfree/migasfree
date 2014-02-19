# -*- coding: utf-8 -*-

import os
import shutil

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.settings import MIGASFREE_REPO_DIR

from migasfree.server.models.common import link
from migasfree.server.models import Version, VersionManager


class Store(models.Model):
    """
    Ubicacion: rutas donde se guardaran los paquetes. P.e. /terceros/vmware
    """
    name = models.CharField(
        _("name"),
        max_length=50
    )

    version = models.ForeignKey(
        Version,
        verbose_name=_("version")
    )

    objects = VersionManager()  # manager by user version

    def create_dir(self):
        _path = os.path.join(
            MIGASFREE_REPO_DIR,
            self.version.name,
            'STORES',
            self.name
        )
        if not os.path.exists(_path):
            os.makedirs(_path)

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "-")
        self.create_dir()
        super(Store, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # remove the directory of Store
        path = os.path.join(
            MIGASFREE_REPO_DIR,
            self.version.name,
            "STORES",
            self.name
        )
        if os.path.exists(path):
            shutil.rmtree(path)
        super(Store, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta():
        app_label = 'server'
        verbose_name = _("Store")
        verbose_name_plural = _("Stores")
        unique_together = (("name", "version"),)
        permissions = (("can_save_store", "Can save Store"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
