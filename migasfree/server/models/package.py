# -*- coding: utf-8 -*-

import os

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from migasfree.server.functions import trans
from migasfree.server.models import (
    Version,
    VersionManager,
    Store,
    MigasLink
)


class Package(models.Model, MigasLink):
    name = models.CharField(
        _("name"),
        max_length=100
    )

    version = models.ForeignKey(
        Version,
        verbose_name=_("version")
    )

    store = models.ForeignKey(
        Store,
        verbose_name=_("store")
    )

    objects = VersionManager()  # manager by user version

    def __init__(self, *args, **kwargs):
        super(Package, self).__init__(*args, **kwargs)

        if self.id:
            info_link = "%sSTORES/%s/%s/?version=%s" % (
                reverse('package_info', args=('', )),
                self.store.name,
                self.name,
                self.version.name
            )

            download_link = '%s%s/STORES/%s/%s' % (
                settings.MEDIA_URL,
                self.version.name,
                self.store.name,
                self.name
            )

            self._actions = [
                [trans('Package Information'), info_link],
                [trans('Download'), download_link]
            ]

    def create_dir(self):
        _path = os.path.join(
            settings.MIGASFREE_REPO_DIR,
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
        verbose_name = _("Package/Set")
        verbose_name_plural = _("Packages/Sets")
        unique_together = (("name", "version"),)
        permissions = (("can_save_package", "Can save Package"),)
