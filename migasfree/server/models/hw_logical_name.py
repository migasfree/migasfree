# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from server.models.computer_login_update_hwnode import HwNode


class HwLogicalName(models.Model):
    node = models.ForeignKey(
        HwNode,
        verbose_name=unicode(_("hardware node"))
    )

    name = models.TextField(
        unicode(_("name")),
        null=False,
        blank=True
    )  # This is the field "logicalname" in lshw

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Hardware Logical Name"))
        verbose_name_plural = unicode(_("Hardware Logical Names"))
