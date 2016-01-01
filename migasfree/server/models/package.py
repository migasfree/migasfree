# -*- coding: utf-8 -*-

import os

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _
from django.conf import settings

from . import Version, Store, MigasLink


class PackageManager(models.Manager):
    def create(self, name, version, store):
        pkg = Package()
        pkg.name = name
        pkg.version = version
        pkg.store = store
        pkg.save()

        return pkg

    def by_version(self, version_id):
        return self.get_queryset().filter(version__id=version_id)


@python_2_unicode_compatible
class Package(models.Model, MigasLink):
    name = models.CharField(
        verbose_name=_("name"),
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

    objects = PackageManager()

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
                [ugettext('Package Information'), info_link],
                [ugettext('Download'), download_link]
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

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Package/Set")
        verbose_name_plural = _("Packages/Sets")
        unique_together = (("name", "version"),)
        permissions = (("can_save_package", "Can save Package"),)
