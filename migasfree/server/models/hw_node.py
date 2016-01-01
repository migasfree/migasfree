# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import Computer, MigasLink


class HwNodeManager(models.Manager):
    def create(self, data):
        obj = HwNode(
            parent=data.get('parent'),
            computer=data.get('computer'),
            level=data.get('level'),
            width=data.get('width'),
            name=data.get('name'),
            classname=data.get('classname'),
            enabled=data.get('enabled', False),
            claimed=data.get('claimed', False),
            description=data.get('description'),
            vendor=data.get('vendor'),
            product=data.get('product'),
            version=data.get('version'),
            serial=data.get('serial'),
            businfo=data.get('businfo'),
            physid=data.get('physid'),
            slot=data.get('slot'),
            size=data.get('size'),
            capacity=data.get('capacity'),
            clock=data.get('clock'),
            dev=data.get('dev')
        )
        obj.save()

        return obj


@python_2_unicode_compatible
class HwNode(models.Model, MigasLink):
    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        verbose_name=_("parent"),
        related_name="child"
    )

    level = models.IntegerField(
        verbose_name=_("level"),
        null=False
    )

    width = models.IntegerField(
        verbose_name=_("width"),
        null=True
    )

    computer = models.ForeignKey(
        Computer,
        verbose_name=_("computer")
    )

    name = models.TextField(
        verbose_name=_("id"),
        null=False,
        blank=True
    )  # This is the field "id" in lshw

    classname = models.TextField(
        verbose_name=_("class"),
        null=False,
        blank=True
    )  # This is the field "class" in lshw

    enabled = models.BooleanField(
        verbose_name=_("enabled"),
        default=False,
    )

    claimed = models.BooleanField(
        verbose_name=_("claimed"),
        default=False,
    )

    description = models.TextField(
        verbose_name=_("description"),
        null=True,
        blank=True
    )

    vendor = models.TextField(
        verbose_name=_("vendor"),
        null=True,
        blank=True
    )

    product = models.TextField(
        verbose_name=_("product"),
        null=True,
        blank=True
    )

    version = models.TextField(
        verbose_name=_("version"),
        null=True,
        blank=True
    )

    serial = models.TextField(
        verbose_name=_("serial"),
        null=True,
        blank=True
    )

    businfo = models.TextField(
        verbose_name=_("businfo"),
        null=True,
        blank=True
    )

    physid = models.TextField(
        verbose_name=_("physid"),
        null=True,
        blank=True
    )

    slot = models.TextField(
        verbose_name=_("slot"),
        null=True,
        blank=True
    )

    size = models.BigIntegerField(
        verbose_name=_("size"),
        null=True
    )

    capacity = models.BigIntegerField(
        verbose_name=_("capacity"),
        null=True
    )

    clock = models.IntegerField(
        verbose_name=_("clock"),
        null=True
    )

    dev = models.TextField(
        verbose_name=_("dev"),
        null=True,
        blank=True
    )

    icon = models.TextField(
        verbose_name=_("icon"),
        null=True,
        blank=True
    )

    objects = HwNodeManager()

    def __str__(self):
        return self.product if self.description and 'lshw' in self.description \
            else '%s: %s' % (self.description, self.product)

    def link(self):
        try:
            return format_html('<a href="%s">%s</a>' % (
                reverse('hardware_resume', args=(self.computer.id,)),
                self.__str__()
            ))
        except:
            return ''

    link.allow_tags = True
    link.short_description = _("Hardware")

    class Meta:
        app_label = 'server'
        verbose_name = _("Hardware Node")
        verbose_name_plural = _("Hardware Nodes")
