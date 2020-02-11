# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import HwNode


class HwLogicalNameManager(models.Manager):
    def create(self, node, name):
        obj = HwLogicalName(
            node=node,
            name=name
        )
        obj.save()

        return obj


class HwLogicalName(models.Model):
    node = models.ForeignKey(
        HwNode,
        on_delete=models.CASCADE,
        verbose_name=_("hardware node")
    )

    name = models.TextField(
        verbose_name=_("name"),
        blank=True
    )  # This is the field "logicalname" in lshw

    objects = HwLogicalNameManager()

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Hardware Logical Name")
        verbose_name_plural = _("Hardware Logical Names")
