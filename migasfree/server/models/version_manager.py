# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User as UserSystem
from django.contrib.auth.models import UserManager
from django.utils.translation import ugettext_lazy as _

from migasfree.middleware import threadlocals

from migasfree.server.models import Version


def user_version():
    """
    Return the user version that logged
    """
    try:
        return UserProfile.objects.get(
            id=threadlocals.get_current_user().id
        ).version
    except:
        return None


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


class UserProfile(UserSystem):
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
