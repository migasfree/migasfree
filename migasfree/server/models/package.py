# -*- coding: utf-8 -*-

import os

from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _
from django.conf import settings

from . import Project, Store, MigasLink


class PackageManager(models.Manager):
    def create(self, name, project, store):
        pkg = Package()
        pkg.name = name
        pkg.project = project
        pkg.store = store
        pkg.save()

        return pkg

    def by_project(self, project_id):
        return self.get_queryset().filter(project__id=project_id)


@python_2_unicode_compatible
class Package(models.Model, MigasLink):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=100
    )

    project = models.ForeignKey(
        Project,
        verbose_name=_("project")
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
                        self.project.name, self.store.name, self.name
                    ),
                )
            )

            download_link = '%s%s/STORES/%s/%s' % (
                settings.MEDIA_URL,
                self.project.name,
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
        path = self.path(self.project.name, self.store.name, self.name)
        if not os.path.exists(path):
            os.makedirs(path)

    def clean(self):
        super(Package, self).clean()

        if not hasattr(self, 'project'):
            return False

        if self.store.project.id != self.project.id:
            raise ValidationError(_('Store must belong to the project'))

        queryset = Package.objects.filter(
            name=self.name
        ).filter(
            project__id=self.project.id
        ).filter(~models.Q(id=self.id))
        if queryset.exists():
            raise ValidationError(_('Duplicated name at project'))

    def save(self, *args, **kwargs):
        self.create_dir()
        super(Package, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Package/Set")
        verbose_name_plural = _("Packages/Sets")
        unique_together = (("name", "project"),)
        permissions = (("can_save_package", "Can save Package"),)
