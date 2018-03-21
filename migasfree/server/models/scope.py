# -*- coding: utf-8 -*-

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .attribute import Attribute
from .domain import Domain
from .userprofile import UserProfile
from .common import MigasLink


class ScopeManager(models.Manager):
    def create(self, user, name, included_attributes, excluded_attributes):
        obj = Scope()
        obj.name = name
        obj.user = user
        obj.included_attributes = included_attributes
        obj.excluded_attributes = excluded_attributes
        obj.save()
        return obj

    def scope(self, user):
        qs = super(ScopeManager, self).get_queryset()
        qs = qs.filter(user=user)
        if user.domain_preference:
            qs = qs.filter(domain=user.domain_preference)

        return qs


@python_2_unicode_compatible
class Scope(models.Model, MigasLink):
    user = models.ForeignKey(
        UserProfile,
        verbose_name=_("user"),
        null=False,
    )

    name = models.CharField(
        max_length=50,
        verbose_name=_('name')
    )

    domain = models.ForeignKey(
        Domain,
        verbose_name=_("domain"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    included_attributes = models.ManyToManyField(
        Attribute,
        related_name="ScopeIncludedAttribute",
        blank=True,
        verbose_name=_("included attributes")
    )

    excluded_attributes = models.ManyToManyField(
        Attribute,
        related_name="ScopeExcludedAttribute",
        blank=True,
        verbose_name=_("excluded attributes")
    )

    objects = ScopeManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        super(Scope, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Scope")
        verbose_name_plural = _("Scopes")
        permissions = (("can_save_scope", "Can save Scope"),)
