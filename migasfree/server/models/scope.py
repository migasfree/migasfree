# -*- coding: utf-8 -*-

from django.db import models
from django.core.exceptions import ValidationError
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

        if not user.is_view_all():
            qs = qs.filter(included_attributes__in=user.get_attributes()).distinct()

        return qs


@python_2_unicode_compatible
class Scope(models.Model, MigasLink):
    user = models.ForeignKey(
        UserProfile,
        verbose_name=_("user"),
        null=False,
        on_delete=models.CASCADE,
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

    def related_objects(self, model, user):
        """
        Return Queryset with the related computers based in attributes
        """
        from migasfree.server.models import Computer, Attribute

        if model == 'computer':
            qs = Computer.productive.scope(user)
            if self.domain:
                qs = qs.filter(
                    sync_attributes__in=Attribute.objects.filter(
                        id__in=self.domain.included_attributes.all()
                    ).exclude(
                        id__in=self.domain.excluded_attributes.all()
                    )
                )

            qs = qs.filter(
                sync_attributes__in=self.included_attributes.all()
            ).exclude(
                sync_attributes__in=self.excluded_attributes.all()
            ).distinct()

            return qs

        return None

    def validate_unique(self, exclude=None):
        if Scope.objects.exclude(id=self.id).filter(
                name=self.name,
                user=self.user,
                domain__isnull=True
        ).exists():
            raise ValidationError(_("Duplicated name"))

        super(Scope, self).validate_unique(exclude)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.name = slugify(self.name)
        super(Scope, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        app_label = 'server'
        verbose_name = _("Scope")
        verbose_name_plural = _("Scopes")
        unique_together = (('name', 'domain', 'user'),)
        permissions = (("can_save_scope", "Can save Scope"),)
