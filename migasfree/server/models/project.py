# -*- coding: utf-8 -*-

import os
import shutil

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import (
    User as UserSystem,
    UserManager
)
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from migasfree.middleware import threadlocals
from . import Pms, Platform, MigasLink


class ProjectManager(models.Manager):
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
    OS Version: 'Ubuntu natty 32bit' or 'openSUSE 12.1' or 'Vitalinux'
    This is 'your personal distribution', a set of computers with a determinate
    Distribution for customize.
    """

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
        return os.path.join(Project.path(name), 'REPOSITORIES')

    @staticmethod
    def stores_path(name):
        return os.path.join(Project.path(name), 'STORES')

    def _create_dirs(self):
        repos = self.repositories_path(self.name)
        if not os.path.exists(repos):
            os.makedirs(repos)

        stores = self.stores_path(self.name)
        if not os.path.exists(stores):
            os.makedirs(stores)

    @staticmethod
    def get_project_names():
        return Project.objects.all().order_by('name').values_list('id', 'name')

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "-")
        self._create_dirs()

        super(Project, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        permissions = (("can_save_project", "Can save Project"),)
        ordering = ['name']


class UserProfile(UserSystem, MigasLink):
    """
    info = 'For change password use <a href="%s">change password form</a>.' \
        % reverse('admin:password_change')
    """

    project = models.ForeignKey(
        Project,
        verbose_name=_("project"),
        null=True,
        on_delete=models.SET_NULL
    )

    objects = UserManager()

    @staticmethod
    def get_logged_project():
        """
        Return the user project that is logged
        # TODO remove this method
        """
        try:
            return UserProfile.objects.get(
                id=threadlocals.get_current_user().id
            ).project
        except:
            return None

    def update_project(self, project):
        self.project = project
        self.save()

    def save(self, *args, **kwargs):
        if not (
            self.password.startswith("sha1$")
            or self.password.startswith("pbkdf2")
        ):
            super(UserProfile, self).set_password(self.password)

        super(UserProfile, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")
        permissions = (("can_save_userprofile", "Can save User Profile"),)


@receiver(pre_delete, sender=Project)
def delete_project(sender, instance, **kwargs):
    path = Project.path(instance.name)
    if os.path.exists(path):
        shutil.rmtree(path)
