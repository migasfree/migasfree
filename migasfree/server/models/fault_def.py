# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models.common import link, LANGUAGES_CHOICES
from migasfree.server.models import Attribute


class FaultDef(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        unique=True
    )

    description = models.TextField(
        unicode(_("description")),
        null=True,
        blank=True
    )

    active = models.BooleanField(
        unicode(_("active")),
        default=True
    )

    language = models.IntegerField(
        unicode(_("programming language")),
        default=0,
        choices=LANGUAGES_CHOICES
    )

    code = models.TextField(
        unicode(_("Code")),
        null=False,
        blank=True
    )

    attributes = models.ManyToManyField(
        Attribute,
        null=True,
        blank=True,
        verbose_name=unicode(_("attributes"))
    )

    def list_attributes(self):
        cattributes = ""
        for i in self.attributes.all():
            cattributes += i.value + ","

        return cattributes[0:len(cattributes) - 1]

    list_attributes.short_description = unicode(_("attributes"))

    def save(self, *args, **kwargs):
        self.code = self.code.replace("\r\n", "\n")
        self.name = self.name.replace(" ", "_")
        super(FaultDef, self).save(*args, **kwargs)

    def namefunction(self):
        return "FAULT_%s" % self.name

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Fault Definition"))
        verbose_name_plural = unicode(_("Faults Definition"))
        permissions = (("can_save_faultdef", "Can save Fault Definition"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
