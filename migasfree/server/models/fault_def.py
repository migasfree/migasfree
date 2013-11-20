# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models.common import link, LANGUAGES_CHOICES
from migasfree.server.models import Attribute
from migasfree.server.models.version_manager import UserProfile


class FaultDef(models.Model):
    name = models.CharField(
        _("name"),
        max_length=50,
        unique=True
    )

    description = models.TextField(
        _("description"),
        null=True,
        blank=True
    )

    active = models.BooleanField(
        _("active"),
        default=True
    )

    language = models.IntegerField(
        _("programming language"),
        default=0,
        choices=LANGUAGES_CHOICES
    )

    code = models.TextField(
        _("Code"),
        null=False,
        blank=True
    )

    attributes = models.ManyToManyField(
        Attribute,
        null=True,
        blank=True,
        verbose_name=_("attributes")
    )

    users = models.ManyToManyField(
        UserProfile,
        null=True,
        blank=True,
        verbose_name=_("users")
    )

    def list_attributes(self):
        cattributes = ""
        for i in self.attributes.all():
            cattributes += i.value + ","

        return cattributes[0:len(cattributes) - 1]

    list_attributes.short_description = _("attributes")

    def list_users(self):
        cusers = ""
        for i in self.users.all():
            cusers += i.username + ","

        return cusers[0:len(cusers) - 1]

    list_users.short_description = _("users")

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
        verbose_name = _("Fault Definition")
        verbose_name_plural = _("Faults Definition")
        permissions = (("can_save_faultdef", "Can save Fault Definition"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
