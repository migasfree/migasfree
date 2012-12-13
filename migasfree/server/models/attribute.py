# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models.common import link
from migasfree.server.models import Property


class Attribute(models.Model):
    property_att = models.ForeignKey(
        Property,
        verbose_name=_("Property of attribute")
    )

    value = models.CharField(
        _("value"),
        max_length=250
    )

    description = models.TextField(
        _("description"),
        null=True,
        blank=True
    )

    def property_link(self):
        return self.property_att.link()

    property_link.short_description = _("Property")
    property_link.allow_tags = True

    def __unicode__(self):
        return u'%s-%s %s' % (
            self.property_att.prefix,
            self.value,
            self.description
        )

    class Meta:
        app_label = 'server'
        verbose_name = _("Attribute")
        verbose_name_plural = _("Attributes")
        unique_together = (("property_att", "value"),)
        permissions = (("can_save_attribute", "Can save Attribute"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
