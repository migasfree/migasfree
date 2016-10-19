# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import DeviceType, DeviceManufacturer, DeviceConnection, MigasLink


@python_2_unicode_compatible
class DeviceModel(models.Model, MigasLink):
    name = models.CharField(
        verbose_name=_("name"),
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
        blank=True,
        verbose_name=_("connections")
    )

    def __str__(self):
        return '%s-%s' % (self.manufacturer, self.name)

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "_")
        super(DeviceModel, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Model")
        verbose_name_plural = _("Models")
        unique_together = (("devicetype", "manufacturer", "name"),)
        permissions = (("can_save_devicemodel", "Can save Device Model"),)
        ordering = ['manufacturer', 'name']
