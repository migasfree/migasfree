# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from common import link


class DeviceType(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Device (Type)"))
        verbose_name_plural = unicode(_("Device (Types)"))
        permissions = (("can_save_devicetype", "Can save Device Type"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
