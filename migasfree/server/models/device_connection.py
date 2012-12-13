# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models.common import link
from migasfree.server.models import DeviceType


class DeviceConnection(models.Model):
    name = models.CharField(
        _("name"),
        max_length=50,
        null=True,
        blank=True
    )

    fields = models.CharField(
        _("fields"),
        max_length=50,
        null=True,
        blank=True
    )  # DEPRECATED

    uri = models.CharField(
        _("uri"),
        max_length=50,
        null=True,
        blank=True
    )

    install = models.TextField(
        _("install"),
        null=True,
        blank=True,
    )  # DEPRECATED

    remove = models.TextField(
        _("remove"),
        null=True,
        blank=True,
    )  # DEPRECATED

    devicetype = models.ForeignKey(
        DeviceType,
        verbose_name=_("device type")
    )

    def __unicode__(self):
        return u'(%s) %s' % (self.devicetype.name, self.name)

    def save(self, *args, **kwargs):
        self.install = self.install.replace("\r\n", "\n")
        self.remove = self.remove.replace("\r\n", "\n")
        super(DeviceConnection, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Device (Connection)")
        verbose_name_plural = _("Device (Connections)")
        unique_together = (("devicetype", "name"),)
        permissions = (("can_save_deviceconnection", "Can save Device Connection"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
