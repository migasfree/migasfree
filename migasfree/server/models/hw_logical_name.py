# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models import HwNode


class HwLogicalName(models.Model):
    node = models.ForeignKey(
        HwNode,
        verbose_name=_("hardware node")
    )

    name = models.TextField(
        _("name"),
        null=False,
        blank=True
    )  # This is the field "logicalname" in lshw

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Hardware Logical Name")
        verbose_name_plural = _("Hardware Logical Names")
