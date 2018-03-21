# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


from . import (
    Property,
    Attribute,
    ServerAttribute,
    MigasLink,
)


@python_2_unicode_compatible
class Domain(models.Model, MigasLink):
    name = models.CharField(
        max_length=50,
        verbose_name=_('name')
    )

    comment = models.TextField(
        verbose_name=_("comment"),
        null=True,
        blank=True
    )

    included_attributes = models.ManyToManyField(
        Attribute,
        related_name="DomainIncludedAttribute",
        blank=True,
        verbose_name=_("included attributes")
    )

    excluded_attributes = models.ManyToManyField(
        Attribute,
        related_name="DomainExcludedAttribute",
        blank=True,
        verbose_name=_("excluded attributes")
    )

    tags = models.ManyToManyField(
        ServerAttribute,
        blank=True,
        verbose_name=_("tags"),
        related_name='domain_tags'
    )

    def __str__(self):
        return self.name

    @staticmethod
    def process(attributes):
        property_set, _ = Property.objects.get_or_create(
            prefix='DMN', sort='server',
            defaults={'name': 'DOMAIN', 'kind': 'R'}
        )

        att_id = []
        for item in Domain.objects.all():
            for att_domain in Domain.objects.filter(
                id=item.id
            ).filter(
                Q(included_attributes__id__in=attributes)
            ).filter(
                ~Q(excluded_attributes__id__in=attributes)
            ).distinct():
                att = Attribute.objects.create(property_set, att_domain.name)
                att_id.append(att.id)

        return att_id

    def save(self, *args, **kwargs):
        self.name = slugify(self.name).upper()
        super(Domain, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Domain")
        verbose_name_plural = _("Domains")
        permissions = (("can_save_domain", "Can save Domain"),)
