# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from . import Attribute, UserProfile, MigasLink


@python_2_unicode_compatible
class FaultDefinition(models.Model, MigasLink):
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

    enabled = models.BooleanField(
        verbose_name=_("enabled"),
        default=True
    )

    language = models.IntegerField(
        verbose_name=_("programming language"),
        default=settings.MIGASFREE_PROGRAMMING_LANGUAGES[0][0],
        choices=settings.MIGASFREE_PROGRAMMING_LANGUAGES
    )

    code = models.TextField(
        verbose_name=_("code"),
        blank=True
    )

    included_attributes = models.ManyToManyField(
        Attribute,
        blank=True,
        verbose_name=_("included attributes")
    )

    excluded_attributes = models.ManyToManyField(
        Attribute,
        related_name="ExcludeAttributeFaultDefinition",
        blank=True,
        verbose_name=_("excluded attributes")
    )

    users = models.ManyToManyField(
        UserProfile,
        blank=True,
        verbose_name=_("users")
    )

    def list_included_attributes(self):
        return self.included_attributes.all().values_list('value', flat=True)

    list_included_attributes.short_description = _("included attributes")

    def list_excluded_attributes(self):
        return self.excluded_attributes.all().values_list('value', flat=True)

    list_excluded_attributes.short_description = _("excluded attributes")

    def list_users(self):
        return self.users.all().values_list('username', flat=True)

    list_users.short_description = _("users")

    @staticmethod
    def enabled_for_attributes(attributes):
        return list(FaultDefinition.objects.filter(
            Q(enabled=True) &
            Q(included_attributes__id__in=attributes) &
            ~Q(excluded_attributes__id__in=attributes)
        ).distinct().values('language', 'name', 'code'))

    def save(self, *args, **kwargs):
        self.code = self.code.replace("\r\n", "\n")
        self.name = self.name.replace(" ", "_")
        super(FaultDefinition, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Fault Definition")
        verbose_name_plural = _("Fault Definitions")
        permissions = (("can_save_faultdefinition", "Can save Fault Definition"),)
        ordering = ['name']
