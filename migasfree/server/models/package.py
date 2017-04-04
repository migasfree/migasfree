# -*- coding: utf-8 -*-

import os

from django.db import models
from django.core.exceptions import ValidationError
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

    def menu_link(self):
        if self.id:
            info_link = reverse(
                'package_info',
                args=(
                    '%s/STORES/%s/%s' % (
                        self.version.name, self.store.name, self.name
                    ),
                )
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
        return super(Package, self).menu_link()

    @staticmethod
    def path(project_name, store_name, name):
        return os.path.join(Store.path(project_name, store_name), name)

    def create_dir(self):
        path = self.path(self.version.name, self.store.name, self.name)
        if not os.path.exists(path):
            os.makedirs(path)

    def clean(self):
        super(Package, self).clean()

        if not hasattr(self, 'version'):
            return False

        if self.store.version.id != self.version.id:
            raise ValidationError(_('Store must belong to the version'))

        queryset = Package.objects.filter(
            name=self.name
        ).filter(
            version__id=self.version.id
        ).filter(~models.Q(id=self.id))
        if queryset.exists():
            raise ValidationError(_('Duplicated name at version'))

    def save(self, *args, **kwargs):
        self.create_dir()
        super(Package, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Package/Set")
        verbose_name_plural = _("Packages/Sets")
        unique_together = (("name", "version"),)
        permissions = (("can_save_package", "Can save Package"),)
