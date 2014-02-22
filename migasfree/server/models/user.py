# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(models.Model):
    name = models.CharField(
        _("name"),
        max_length=50,
        unique=True
    )

    fullname = models.CharField(
        _("fullname"),
        max_length=100
    )

    def __unicode__(self):
        return u'%s - %s' % (self.name, self.fullname)

    class Meta:
        app_label = 'server'
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        permissions = (("can_save_user", "Can save User"),)
