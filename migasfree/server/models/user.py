# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from common import link


class User(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        unique=True
    )

    fullname = models.CharField(
        unicode(_("fullname")),
        max_length=100
    )

    def __unicode__(self):
        return u'%s - %s' % (self.name, self.fullname)

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("User"))
        verbose_name_plural = unicode(_("Users"))
        permissions = (("can_save_user", "Can save User"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
