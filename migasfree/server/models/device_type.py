# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class DeviceType(models.Model):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Type")
        verbose_name_plural = _("Types")
        permissions = (("can_save_devicetype", "Can save Device Type"),)
