# -*- coding: utf-8 -*-

import os

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from migasfree.settings import STATIC_URL, MIGASFREE_REPO_DIR

from server.models.version import Version
from server.models.version_manager import VersionManager
from server.models.store import Store


class Package(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=100
    )

    version = models.ForeignKey(
        Version,
        verbose_name=unicode(_("version"))
    )

    store = models.ForeignKey(
        Store,
        verbose_name=unicode(_("store"))
    )

    objects = VersionManager()  # manager by user version

    def create_dir(self):
        _path = os.path.join(
            MIGASFREE_REPO_DIR,
            self.version.name,
            'STORES',
            self.store.name,
            self.name
        )
        if not os.path.exists(_path):
            os.makedirs(_path)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Package/Set"))
        verbose_name_plural = unicode(_("Packages/Sets"))
        unique_together = (("name", "version"),)
        permissions = (("can_save_package", "Can save Package"),)

    def link(self):
        info = "%s/STORES/%s/%s/?version=%s" % (
            reverse('package_info'),
            self.store.name,
            self.name,
            self.version.name
        )

        return '<a href="%s"><img src="%sicons/package-info.png" height="16px" alt="information" /></a> <a href="%s">%s</a>' % (
            info,
            STATIC_URL,
            reverse('admin:server_package_change', args=(self.id, )),
            self.__unicode__()
        )

    link.short_description = Meta.verbose_name
    link.allow_tags = True
