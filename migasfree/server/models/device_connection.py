# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import DeviceType, MigasLink


class DeviceConnection(models.Model, MigasLink):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=50
    )

    fields = models.CharField(
        verbose_name=_("fields"),
        max_length=100,
        null=True,
        blank=True,
        help_text=_("Fields separated by comma")
    )

    device_type = models.ForeignKey(
        DeviceType,
        on_delete=models.CASCADE,
        verbose_name=_("device type")
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Connection")
        verbose_name_plural = _("Connections")
        unique_together = (("device_type", "name"),)
        permissions = (
            ("can_save_deviceconnection", "Can save Device Connection"),
        )
