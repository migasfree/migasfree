# -*- coding: utf-8 -*-

import json

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models import DeviceConnection, DeviceModel
from migasfree.server.functions import add_default_device_logical


class Device(models.Model):
    name = models.CharField(
        _("name"),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    model = models.ForeignKey(
        DeviceModel,
        verbose_name=_("model")
    )

    connection = models.ForeignKey(
        DeviceConnection,
        verbose_name=_("connection")
    )

    data = models.TextField(
        _("data"),
        null=True,
        blank=False,
        default="{}"
    )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super(Device, self).save(*args, **kwargs)

        if is_new:
            add_default_device_logical(self)

        for device_logical in self.devicelogical_set.all():
            device_logical.reinstall()

    def datadict(self):
        return {
            'name': self.name,
            'model': self.model.name,
            self.connection.name: json.loads(self.data),
        }

    def __unicode__(self):
        return u'%s-%s-%s' % (self.name, self.model.name, self.connection.name)

    class Meta:
        app_label = 'server'
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        unique_together = (("connection", "name"),)
        permissions = (("can_save_device", "Can save Device"),)
