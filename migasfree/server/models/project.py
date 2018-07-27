# -*- coding: utf-8 -*-

import os
import shutil

from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import Pms, Platform, MigasLink


class DomainProjectManager(models.Manager):
    def scope(self, user):
        qs = super(DomainProjectManager, self).get_queryset()
        if not user.is_view_all():
            qs = qs.filter(id__in=user.get_projects())
        return qs


class ProjectManager(DomainProjectManager):
    def create(self, name, pms, platform, auto_register_computers=False):
        obj = Project()
        obj.name = name
        obj.pms = pms
        obj.platform = platform
        obj.auto_register_computers = auto_register_computers
        obj.save()

        return obj


@python_2_unicode_compatible
class Project(models.Model, MigasLink):
    """
    Your Distro: 'Ubuntu natty 32bit' or 'openSUSE 12.1' or 'Vitalinux'
    This is 'your personal distribution', a set of computers with a determinate
    Distribution for customize.
    """

    REPOSITORY_TRAILING_PATH = 'REPOSITORIES'
    STORE_TRAILING_PATH = 'STORES'

    name = models.CharField(
        verbose_name=_("name"),
        max_length=50,
        unique=True
    )

    pms = models.ForeignKey(
        Pms,
        on_delete=models.CASCADE,
        verbose_name=_("package management system")
    )

    auto_register_computers = models.BooleanField(
        verbose_name=_("auto register computers"),
        default=False,
        help_text=_("Is not needed a user for register computers in "
                    "database and get the keys.")
    )

    platform = models.ForeignKey(
        Platform,
        on_delete=models.CASCADE,
        verbose_name=_("platform")
    )

    objects = ProjectManager()

    def __str__(self):
        return self.name

    @staticmethod
    def path(name):
        return os.path.join(settings.MIGASFREE_PUBLIC_DIR, name)

    @staticmethod
    def repositories_path(name):
        return os.path.join(
            Project.path(name),
            Project.REPOSITORY_TRAILING_PATH
        )

    @staticmethod
    def stores_path(name):
        return os.path.join(
            Project.path(name),
            Project.STORE_TRAILING_PATH
        )

    def _create_dirs(self):
        repos = self.repositories_path(self.name)
        if not os.path.exists(repos):
            os.makedirs(repos)

        stores = self.stores_path(self.name)
        if not os.path.exists(stores):
            os.makedirs(stores)

    @staticmethod
    def get_project_names():
        return Project.objects.values_list('id', 'name').order_by('name')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.name = self.name.replace(" ", "-")
        self._create_dirs()

        super(Project, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        app_label = 'server'
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        permissions = (("can_save_project", "Can save Project"),)
        ordering = ['name']


@receiver(pre_delete, sender=Project)
def delete_project(sender, instance, **kwargs):
    path = Project.path(instance.name)
    if os.path.exists(path):
        shutil.rmtree(path)
