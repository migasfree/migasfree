# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import Attribute, LANGUAGES_CHOICES, UserProfile, MigasLink


@python_2_unicode_compatible
class FaultDef(models.Model, MigasLink):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=50,
        unique=True
    )

    description = models.TextField(
        verbose_name=_("description"),
        null=True,
        blank=True
    )

    active = models.BooleanField(
        verbose_name=_("active"),
        default=True
    )

    language = models.IntegerField(
        verbose_name=_("programming language"),
        default=0,
        choices=LANGUAGES_CHOICES
    )

    code = models.TextField(
        verbose_name=_("Code"),
        null=False,
        blank=True
    )

    attributes = models.ManyToManyField(
        Attribute,
        blank=True,
        verbose_name=_("attributes")
    )

    users = models.ManyToManyField(
        UserProfile,
        blank=True,
        verbose_name=_("users")
    )

    def list_attributes(self):
        return ', '.join(self.attributes.all().values_list('value', flat=True))

    list_attributes.short_description = _("attributes")

    def list_users(self):
        return ', '.join(self.users.all().values_list('username', flat=True))

    list_users.short_description = _("users")

    def save(self, *args, **kwargs):
        self.code = self.code.replace("\r\n", "\n")
        self.name = self.name.replace(" ", "_")
        super(FaultDef, self).save(*args, **kwargs)

    def namefunction(self):
        return "FAULT_%s" % self.name

    def __str__(self):
        return self.name

    @staticmethod
    def enabled_for_attributes(attributes):
        return FaultDef.objects.filter(
            models.Q(active=True) &
            models.Q(attributes__id__in=attributes)
        ).distinct().values('language', 'name', 'code')
        # NOTE .distinct('id') NOT supported in sqlite

    class Meta:
        app_label = 'server'
        verbose_name = _("Fault Definition")
        verbose_name_plural = _("Fault Definitions")
        permissions = (("can_save_faultdef", "Can save Fault Definition"),)
        ordering = ['name']
