# -*- coding: utf-8 -*-

import os
import shutil

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import (
    User as UserSystem,
    UserManager
)
from django.conf import settings

from migasfree.server.models import Pms, Platform, MigasLink

from migasfree.middleware import threadlocals


class Version(models.Model, MigasLink):
    """
    Version of S.O. by example 'Ubuntu natty 32bit' or 'AZLinux-2'
    This is 'your distribution', a set of computers with a determinate
    Distribution for personalize.
    """
    name = models.CharField(
        _("name"),
        max_length=50,
        unique=True
    )

    pms = models.ForeignKey(
        Pms,
        verbose_name=_("package management system")
    )

    computerbase = models.CharField(
        _("Actual line computer"),
        max_length=50,
        help_text=_("Computer with the actual line software"),
        default="---"
    )

    base = models.TextField(
        _("Actual line packages"),
        null=False,
        blank=True,
        help_text=_("List ordered of packages of actual line computer")
    )

    autoregister = models.BooleanField(
        _("autoregister"),
        default=False,
        help_text=_("Is not neccesary a user for register the computer in \
                     database and get the keys.")
    )

    platform = models.ForeignKey(
        Platform,
        verbose_name=_("platform")
    )

    def __unicode__(self):
        return self.name

    def create_dirs(self):
        _repos = os.path.join(
            settings.MIGASFREE_REPO_DIR,
            self.name,
            'REPOSITORIES'
        )
        if not os.path.exists(_repos):
            os.makedirs(_repos)

        _stores = os.path.join(
            settings.MIGASFREE_REPO_DIR,
            self.name,
            'STORES'
        )
        if not os.path.exists(_stores):
            os.makedirs(_stores)

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "-")
        self.create_dirs()
        self.base = self.base.replace("\r\n", "\n")

        super(Version, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        path = os.path.join(settings.MIGASFREE_REPO_DIR, self.name)
        if os.path.exists(path):
            shutil.rmtree(path)

        super(Version, self).delete(*args, **kwargs)

    def link(self):
        current_version = user_version()
        if current_version is None:
            current_version_id = 0
        else:
            current_version_id = current_version.id

        return super(Version, self).link(
            default=(self.id != current_version_id)
        )

    link.allow_tags = True
    link.short_description = _("Version")

    class Meta:
        app_label = 'server'
        verbose_name = _("Version")
        verbose_name_plural = _("Versions")
        permissions = (("can_save_version", "Can save Version"),)


class VersionManager(models.Manager):
    """
    VersionManager is used for filter the property "objects" of several
    classes by the version of user logged.
    """
    def get_query_set(self):
        user = user_version()
        if user is None:
            return self.version(0)
        else:
            return self.version(user)

    def version(self, version):
        if version == 0:  # return the objects of ALL VERSIONS
            return super(VersionManager, self).get_query_set()
        else:  # return only the objects of this VERSION
            return super(VersionManager, self).get_query_set().filter(
                version=version
            )


class UserProfile(UserSystem, MigasLink):
    """
    info = 'For change password use <a href="%s">change password form</a>.' \
        % reverse('admin:password_change')
    """

    version = models.ForeignKey(
        Version,
        verbose_name=_("version"),
        null=True,
        on_delete=models.SET_NULL
    )

    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

    def save(self, *args, **kwargs):
        if not (self.password.startswith("sha1$") or
                self.password.startswith("pbkdf2")):
            super(UserProfile, self).set_password(self.password)
        super(UserProfile, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")
        permissions = (("can_save_userprofile", "Can save User Profile"),)


def get_version_names():
    result = []
    for item in Version.objects.all().order_by("name"):
        result.append([item.id, item.name])

    return result


def user_version():
    """
    Return the user version that is logged
    """
    try:
        return UserProfile.objects.get(
            id=threadlocals.get_current_user().id
        ).version
    except:
        return None
