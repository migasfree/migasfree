# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from common import link


class DeviceFile(models.Model):
    name = models.FileField(upload_to="devices")

    def __unicode__(self):
        return u'%s' % (str(self.name).split("/")[-1])

    class Meta:
        app_label = 'server'
        verbose_name = _("Device (File)")
        verbose_name_plural = _("Device (Files)")
        permissions = (("can_save_devicefile", "Can save Device File"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
