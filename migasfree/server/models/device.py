# -*- coding: utf-8 -*-

import json

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import DeviceConnection, DeviceModel, MigasLink


@python_2_unicode_compatible
class Device(models.Model, MigasLink):
    name = models.CharField(
        verbose_name=_("name"),
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
        verbose_name=_("data"),
        null=True,
        blank=False,
        default="{}"
    )

    def location(self):
        data = json.loads(self.data)
        if 'LOCATION' in data:
            return data['LOCATION']
        else:
            return ""

    def model_link(self):
        return self.model.link()

    model_link.short_description = _("Device Model")
    model_link.allow_tags = True

    def datadict(self):
        return {
            'name': self.name,
            'model': self.model.name,
            self.connection.name: json.loads(self.data),
        }

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        unique_together = (("connection", "name"),)
        permissions = (("can_save_device", "Can save Device"),)
