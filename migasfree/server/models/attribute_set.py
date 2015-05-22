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
        _("name"),
        max_length=50
    )

    active = models.BooleanField(
        _("active"),
        default=True,
    )

    attributes = models.ManyToManyField(
        Attribute,
        null=True,
        blank=True,
        verbose_name=_("attributes"),
        help_text=_("Assigned Attributes")
    )

    excludes = models.ManyToManyField(
        Attribute,
        related_name="ExcludeAttributeGroup",
        null=True,
        blank=True,
        verbose_name=_("excludes"),
        help_text=_("Excluded Attributes")
    )

    def save(self, *args, **kwargs):
        # Create a Attributte
        try:
            att = Attribute.objects.get(property_att=Property(id=1), value=self.name)
        except:
            att = Attribute()
            att.value = self.name
            att.property_att = Property(id=1)
            att.description = ""
            att.save()

        super(AttributeSet, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Attributes Set")
        verbose_name_plural = _("Attributes Sets")
        permissions = (("can_save_attributteset", "Can save Attributes Set"),)