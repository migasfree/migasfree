# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models import (
    DeviceType, DeviceManufacturer, DeviceConnection, MigasLink
)


class DeviceModel(models.Model, MigasLink):
    name = models.CharField(
        _("name"),
        max_length=50,
        null=True,
        blank=True
    )

    manufacturer = models.ForeignKey(
        DeviceManufacturer,
        verbose_name=_("manufacturer")
    )

    devicetype = models.ForeignKey(
        DeviceType,
        verbose_name=_("type")
    )

    connections = models.ManyToManyField(
        DeviceConnection,
        null=True,
        blank=True,
        verbose_name=_("connections")
    )

    def __unicode__(self):
        return u'%s-%s' % (str(self.manufacturer), str(self.name))

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "_")
        super(DeviceModel, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Device (Model)")
        verbose_name_plural = _("Device (Models)")
        unique_together = (("devicetype", "manufacturer", "name"),)
        permissions = (("can_save_devicemodel", "Can save Device Model"),)
