# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models import Property, MigasLink
#from migasfree.server.models import Login


class Attribute(models.Model, MigasLink):
    property_att = models.ForeignKey(
        Property,
        verbose_name=_("Property")
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

    _exclude_links = ["computer - tags", ]

    def property_link(self):
        return self.property_att.link()

    property_link.short_description = _("Property")
    property_link.allow_tags = True

    def __unicode__(self):
        return u'%s-%s' % (
            self.property_att.prefix,
            self.value,
        )

    def total_computers(self, version=None):
        from migasfree.server.models import Login
        if version:
            return Login.objects.filter(attributes__id=self.id, computer__version_id=version.id).count()
        else:
            return Login.objects.filter(attributes__id=self.id).count()

    def delete(self, *args, **kwargs):
        # Not allowed delete atributte of ALL, CID, and MID Property.prefix
        if self.property_att.prefix not in ["ALL", "CID", "MID"]:
            super(Attribute, self).delete(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Attribute")
        verbose_name_plural = _("Attributes")
        unique_together = (("property_att", "value"),)
        permissions = (("can_save_attribute", "Can save Attribute"),)


class Tag(Attribute):
    _include_links = ["computer - tags", ]

    class Meta:
        app_label = 'server'
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        proxy = True


class Att(Attribute):

    class Meta:
        app_label = 'server'
        verbose_name = _("Attribute/Tag")
        verbose_name_plural = _("Attributes/Tags")
        proxy = True