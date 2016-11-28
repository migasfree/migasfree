# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import Property, MigasLink


class AttributeManager(models.Manager):
    def create(self, property_att, value, description=None):
        """
        if value = "text~other", description = "other"
        """
        if '~' in value:
            value, description = value.split('~')

        value = value.strip()  # clean field

        queryset = Attribute.objects.filter(
            property_att=property_att, value=value
        )

        if queryset.exists():
            return queryset[0]

        if property_att.auto is False:
            raise ValidationError(
                _('The attribute can not be created because'
                  ' it prevents property')
            )

        obj = Attribute()
        obj.property_att = property_att
        obj.value = value
        obj.description = description
        obj.save()

        return obj


@python_2_unicode_compatible
class Attribute(models.Model, MigasLink):
    property_att = models.ForeignKey(
        Property,
        verbose_name=_("Property")
    )

    value = models.CharField(
        verbose_name=_("value"),
        max_length=250
    )

    description = models.TextField(
        verbose_name=_("description"),
        null=True,
        blank=True
    )

    _exclude_links = ["computer - tags"]

    objects = AttributeManager()

    TOTAL_COMPUTER_QUERY = "SELECT COUNT(server_login.id) \
        FROM server_login,server_login_attributes  \
        WHERE server_attribute.id=server_login_attributes.attribute_id \
        AND server_login_attributes.login_id=server_login.id"

    def property_link(self):
        return self.property_att.link()

    property_link.short_description = _("Property")
    property_link.allow_tags = True

    def __str__(self):
        if self.property_att.prefix == "CID" and \
                settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0] != "id":
            return '%s (CID-%s)' % (self.description, self.value)
        else:
            return '%s-%s' % (self.property_att.prefix, self.value)

    def total_computers(self, version=None):
        from . import Login
        if version:
            return Login.objects.filter(
                attributes__id=self.id,
                computer__version_id=version.id
            ).count()
        else:
            return Login.objects.filter(attributes__id=self.id).count()

    total_computers.admin_order_field = 'total_computers'

    def update_description(self, new_value):
        if self.description != new_value:
            self.description = new_value
            self.save()

    def delete(self, *args, **kwargs):
        # Not allowed delete attribute 'SET-ALL SYSTEM' or CID Property.prefix
        if not (self.property_att.prefix in ["CID", ] or self.id == 1):
            super(Attribute, self).delete(*args, **kwargs)

    @staticmethod
    def process_kind_property(property_att, value):
        attributes = []
        try:
            if property_att.kind == "N":  # Normal
                obj = Attribute.objects.create(property_att, value)
                attributes.append(obj.id)

            if property_att.kind == "-":  # List
                lst = value.split(",")
                for item in lst:
                    item = item.replace('\n', '')
                    if item:
                        obj = Attribute.objects.create(property_att, item)
                        attributes.append(obj.id)

            if property_att.kind == "R":  # Adds right
                lst = value.split(".")
                pos = 0
                for item in lst:
                    obj = Attribute.objects.create(property_att, value[pos:])
                    attributes.append(obj.id)
                    pos += len(item) + 1

            if property_att.kind == "L":  # Adds left
                lst = value.split(".")
                pos = 0
                for item in lst:
                    pos += len(item) + 1
                    obj = Attribute.objects.create(
                        property_att, value[0:pos - 1]
                    )
                    attributes.append(obj.id)
        except:
            pass

        return attributes

    class Meta:
        app_label = 'server'
        verbose_name = _("Attribute/Tag")
        verbose_name_plural = _("Attributes/Tags")
        unique_together = (("property_att", "value"),)
        permissions = (("can_save_attribute", "Can save Attribute"),)
        ordering = ['property_att__prefix', 'value']


class TagManager(AttributeManager):
    def get_queryset(self):
        return super(TagManager, self).get_queryset().filter(
            property_att__tag=True
        )


class Tag(Attribute):
    objects = TagManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('property_att').verbose_name = _("Tag Type")
        super(Tag, self).__init__(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        proxy = True


class FeatureManager(AttributeManager):
    def get_queryset(self):
        return super(FeatureManager, self).get_queryset().filter(
            property_att__tag=False
        )


class Feature(Attribute):
    objects = FeatureManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('property_att').verbose_name = _("Property")
        super(Feature, self).__init__(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Attribute")
        verbose_name_plural = _("Attributes")
        proxy = True
