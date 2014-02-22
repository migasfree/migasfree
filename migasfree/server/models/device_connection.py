# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

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
        max_length=100,
        null=True,
        blank=True,
        help_text=_("Fields separated by comma")
    )

    devicetype = models.ForeignKey(
        DeviceType,
        verbose_name=_("device type")
    )

    def __unicode__(self):
        return u'(%s) %s' % (self.devicetype.name, self.name)

    class Meta:
        app_label = 'server'
        verbose_name = _("Device (Connection)")
        verbose_name_plural = _("Device (Connections)")
        unique_together = (("devicetype", "name"),)
        permissions = (
            ("can_save_deviceconnection", "Can save Device Connection"),
        )
