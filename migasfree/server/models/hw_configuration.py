# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import HwNode


class HwConfigurationManager(models.Manager):
    def create(self, node, name, value):
        obj = HwConfiguration(
            node=node,
            name=name,
            value=value
        )
        obj.save()

        return obj


class HwConfiguration(models.Model):
    node = models.ForeignKey(
        HwNode,
        on_delete=models.CASCADE,
        verbose_name=_("hardware node")
    )

    name = models.TextField(
        verbose_name=_("name"),
        blank=True
    )  # This is the field "config" in lshw

    value = models.TextField(
        verbose_name=_("value"),
        null=True,
        blank=True
    )

    objects = HwConfigurationManager()

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Hardware Configuration")
        verbose_name_plural = _("Hardware Configurations")
        unique_together = (("name", "node"),)
