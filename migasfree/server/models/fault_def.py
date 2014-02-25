# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models import Attribute, LANGUAGES_CHOICES, UserProfile


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
        attributes = ""
        for item in self.attributes.all():
            attributes += item.value + ', '

        return attributes[0:len(attributes) - 2]  # remove trailing ', '

    list_attributes.short_description = _("attributes")

    def list_users(self):
        users = ""
        for item in self.users.all():
            users += item.username + ', '

        return users[0:len(users) - 2]  # remove trailing ', '

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
