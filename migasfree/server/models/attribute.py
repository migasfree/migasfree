# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
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

        if property_att.auto_add is False:
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

    TOTAL_COMPUTER_QUERY = "SELECT COUNT(server_computer.id) \
        FROM server_computer, server_computer_sync_attributes \
        WHERE server_attribute.id=server_computer_sync_attributes.attribute_id \
        AND server_computer_sync_attributes.computer_id=server_computer.id"

    def __str__(self):
        if self.property_att.prefix == 'CID' and \
                settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0] != 'id':
            return u'{} (CID-{})'.format(self.description, self.value)
        else:
            return u'{}-{}'.format(self.property_att.prefix, self.value)

    def total_computers(self, version=None):
        from . import Computer

        queryset = Computer.objects.filter(sync_attributes__id=self.id)
        if version:
            queryset = queryset.filter(version_id=version.id)

        return queryset.count()

    total_computers.admin_order_field = 'total_computers'
    total_computers.short_description = _('Total computers')

    def update_value(self, new_value):
        if self.value != new_value:
            self.value = new_value
            self.save()

    def update_description(self, new_value):
        if self.description != new_value:
            self.description = new_value
            self.save()

    def delete(self, using=None, keep_parents=False):
        # Not allowed delete attribute of basic properties
        if self.property_att.sort != 'basic':
            return super(Attribute, self).delete(using, keep_parents)

    @staticmethod
    def process_kind_property(property_att, value):
        attributes = []

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

        return attributes

    class Meta:
        app_label = 'server'
        verbose_name = _("Attribute")
        verbose_name_plural = _("Attributes")
        unique_together = (("property_att", "value"),)
        permissions = (("can_save_attribute", "Can save Attribute"),)
        ordering = ['property_att__prefix', 'value']


class ServerAttributeManager(AttributeManager):
    def get_queryset(self):
        return super(ServerAttributeManager, self).get_queryset().filter(
            property_att__sort='server'
        )


class ServerAttribute(Attribute):  # Tag
    objects = ServerAttributeManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('property_att').verbose_name = _("Tag Category")
        super(ServerAttribute, self).__init__(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        proxy = True


class ClientAttributeManager(AttributeManager):
    def get_queryset(self):
        return super(ClientAttributeManager, self).get_queryset().filter(
            Q(property_att__sort='client') | Q(property_att__sort='basic')
        )


class ClientAttribute(Attribute):  # Feature
    objects = ClientAttributeManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('property_att').verbose_name = _("Formula")
        super(ClientAttribute, self).__init__(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Attribute")  # FIXME
        verbose_name_plural = _("Attributes")  # FIXME
        proxy = True


class BasicAttributeManager(AttributeManager):
    def get_queryset(self):
        return super(BasicAttributeManager, self).get_queryset().filter(
            property_att__sort='basic'
        )


class BasicAttribute(Attribute):
    objects = BasicAttributeManager()

    @staticmethod
    def process(**kwargs):
        properties = dict(Property.objects.filter(
            enabled=True, sort='basic'
        ).values_list('prefix', 'id'))

        att_id = []

        if 'SET' in properties.keys():
            obj = Attribute.objects.create(
                Property.objects.get(pk=properties['SET']),
                'All Systems'
            )
            att_id.append(obj.id)

        if 'CID' in properties.keys() and 'id' in kwargs:
            obj = Attribute.objects.create(
                Property.objects.get(pk=properties['CID']),
                str(kwargs['id']),
                u'{}~{}'.format(kwargs['id'], kwargs['description'])
            )
            obj.update_description(kwargs['description'])
            att_id.append(obj.id)

        if 'PLT' in properties.keys() and 'platform' in kwargs:
            obj = Attribute.objects.create(
                Property.objects.get(pk=properties['PLT']),
                kwargs['platform']
            )
            att_id.append(obj.id)

        if 'IP' in properties.keys() and 'ip_address' in kwargs:
            obj = Attribute.objects.create(
                Property.objects.get(pk=properties['IP']),
                kwargs['ip_address']
            )
            att_id.append(obj.id)

        if 'VER' in properties.keys() and 'version' in kwargs:
            obj = Attribute.objects.create(
                Property.objects.get(pk=properties['VER']),
                kwargs['version']
            )
            att_id.append(obj.id)

        if 'USR' in properties.keys() and 'user' in kwargs:
            obj = Attribute.objects.create(
                Property.objects.get(pk=properties['USR']),
                kwargs['user']
            )
            att_id.append(obj.id)

        return att_id

    class Meta:
        verbose_name = _("Basic Attribute")
        verbose_name_plural = _("Basic Attributes")
        proxy = True
