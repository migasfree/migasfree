# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from common import link


class DeviceManufacturer(models.Model):
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
        verbose_name = unicode(_("Device (Manufacturer)"))
        verbose_name_plural = unicode(_("Device (Manufacturers)"))
        permissions = (("can_save_devicemanufacturer", "Can save Device Manufacturer"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
