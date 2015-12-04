# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import HwNode


class HwCapabilityManager(models.Manager):
    def create(self, node, name, description):
        obj = HwCapability(
            node=node,
            name=name,
            description=description
        )
        obj.save()

        return obj


class HwCapability(models.Model):
    node = models.ForeignKey(
        HwNode,
        verbose_name=_("hardware node")
    )

    name = models.TextField(
        verbose_name=_("name"),
        null=False,
        blank=True
    )  # This is the field "capability" in lshw

    description = models.TextField(
        verbose_name=_("description"),
        null=True,
        blank=True
    )

    objects = HwCapabilityManager()

    def __unicode__(self):
        ret = self.name
        if self.description:
            ret += ': %s' % self.description

        return ret

    class Meta:
        app_label = 'server'
        verbose_name = _("Hardware Capability")
        verbose_name_plural = _("Hardware Capabilities")
        unique_together = (("name", "node"),)
