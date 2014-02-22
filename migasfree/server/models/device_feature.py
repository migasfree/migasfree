# -*- coding: utf-8 *-*

from django.db import models
from django.utils.translation import ugettext_lazy as _


class DeviceFeature(models.Model):
    name = models.CharField(
        _("name"),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Device (Feature)")
        verbose_name_plural = _("Device (Feature)")
        permissions = (("can_save_devicefeature", "Can save Device Feature"),)
