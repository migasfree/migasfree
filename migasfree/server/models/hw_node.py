# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models import Computer, MigasLink


class HwNode(models.Model, MigasLink):
    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        verbose_name=_("parent"),
        related_name="child"
    )

    level = width = models.IntegerField(
        _("width"),
        null=False
    )

    width = models.IntegerField(
        _("width"),
        null=True
    )

    computer = models.ForeignKey(
        Computer,
        verbose_name=_("computer")
    )

    name = models.TextField(
        _("id"),
        null=False,
        blank=True
    )  # This is the field "id" in lshw

    classname = models.TextField(
        _("class"),
        null=False,
        blank=True
    )  # This is the field "class" in lshw

    enabled = models.BooleanField(
        _("enabled"),
        default=False,
    )

    claimed = models.BooleanField(
        _("claimed"),
        default=False,
    )

    description = models.TextField(
        _("description"),
        null=True,
        blank=True
    )

    vendor = models.TextField(
        _("vendor"),
        null=True,
        blank=True
    )

    product = models.TextField(
        _("product"),
        null=True,
        blank=True
    )

    version = models.TextField(
        _("version"),
        null=True,
        blank=True
    )

    serial = models.TextField(
        _("serial"),
        null=True,
        blank=True
    )

    businfo = models.TextField(
        _("businfo"),
        null=True,
        blank=True
    )

    physid = models.TextField(
        _("physid"),
        null=True,
        blank=True
    )

    slot = models.TextField(
        _("slot"),
        null=True,
        blank=True
    )

    size = models.BigIntegerField(
        _("size"),
        null=True
    )

    capacity = models.BigIntegerField(
        _("capacity"),
        null=True
    )

    clock = models.IntegerField(
        _("clock"),
        null=True
    )

    dev = models.TextField(
        _("dev"),
        null=True,
        blank=True
    )

    icon = models.TextField(
        _("icon"),
        null=True,
        blank=True
    )

    def __unicode__(self):
        return self.product

    def link(self, default=True):
        try:
            return format_html('<a href="%s">%s</a>' % (
                reverse('hardware_resume', args=(self.computer.id, )),
                self.__unicode__()
            ))
        except:
            return ''

    link.allow_tags = True
    link.short_description = _("Hardware")

    class Meta:
        app_label = 'server'
        verbose_name = _("Hardware Node")
        verbose_name_plural = _("Hardware Nodes")
