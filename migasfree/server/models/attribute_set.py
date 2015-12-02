# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models import (
    Property,
    Attribute,
    MigasLink
)


class AttributeSet(models.Model, MigasLink):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=50
    )

    active = models.BooleanField(
        verbose_name=_("active"),
        default=True,
    )

    attributes = models.ManyToManyField(
        Attribute,
        blank=True,
        verbose_name=_("attributes"),
        help_text=_("Assigned Attributes")
    )

    excludes = models.ManyToManyField(
        Attribute,
        related_name="ExcludeAttributeGroup",
        blank=True,
        verbose_name=_("excludes"),
        help_text=_("Excluded Attributes")
    )

    def save(self, *args, **kwargs):
        Attribute.objects.get_or_create(
            property_att=Property(id=1),
            value=self.name,
            defaults={'description': ''}
        )

        super(AttributeSet, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Attributes Set")
        verbose_name_plural = _("Attributes Sets")
        permissions = (("can_save_attributteset", "Can save Attributes Set"),)
