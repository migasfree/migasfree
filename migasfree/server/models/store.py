# -*- coding: utf-8 -*-

import os
import shutil

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings

from . import Version, MigasLink


class StoreManager(models.Manager):
    def create(self, name, version):
        obj = Store()
        obj.name = name
        obj.version = version
        obj.save()

        return obj

    def by_version(self, version_id):
        return self.get_queryset().filter(version__id=version_id)


@python_2_unicode_compatible
class Store(models.Model, MigasLink):
    """
    Location where packages will be stored (p.e. /third/vmware)
    """
    name = models.CharField(
        verbose_name=_("name"),
        max_length=50
    )

    version = models.ForeignKey(
        Version,
        verbose_name=_("version")
    )

    objects = StoreManager()

    def menu_link(self):
        if self.id:
            info_link = reverse(
                'package_info',
                args=('%s/STORES/%s/' % (self.version.name, self.name),)
            )

            download_link = '%s%s/STORES/%s/' % (
                settings.MEDIA_URL,
                self.version.name,
                self.name
            )

            self._actions = [
                [ugettext('Package Information'), info_link],
                [ugettext('Download'), download_link]
            ]

        return super(Store, self).menu_link()

    def create_dir(self):
        _path = os.path.join(
            settings.MIGASFREE_REPO_DIR,
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
            settings.MIGASFREE_REPO_DIR,
            self.version.name,
            "STORES",
            self.name
        )
        if os.path.exists(path):
            shutil.rmtree(path)

        super(Store, self).delete(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Store")
        verbose_name_plural = _("Stores")
        unique_together = (("name", "version"),)
        permissions = (("can_save_store", "Can save Store"),)
        ordering = ['name', 'version']
