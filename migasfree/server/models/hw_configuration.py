# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models import HwNode


class HwConfiguration(models.Model):
    node = models.ForeignKey(
        HwNode,
        verbose_name=_("hardware node")
    )

    name = models.TextField(
        _("name"),
        null=False,
        blank=True
    )  # This is the field "config" in lshw

    value = models.TextField(
        _("value"),
        null=True,
        blank=True
    )

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Hardware Capability")
        verbose_name_plural = _("Hardware Capabilities")
        unique_together = (("name", "node"),)
