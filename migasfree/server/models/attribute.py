# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import Property, MigasLink
from .notification import Notification


class DomainAttributeManager(models.Manager):
    def scope(self, user):
        qs = super(DomainAttributeManager, self).get_queryset()
        if not user.is_view_all():
            qs = qs.filter(
                Q(id__in=user.get_attributes()) |
                Q(id__in=user.get_domain_tags())
            )

        return qs.defer(
            'computer__software_inventory',
            'computer__software_history'
        )


class AttributeManager(DomainAttributeManager):
    def create(self, property_att, value, description=None):
        """
        if value = "text~other", description = "other"
        """

        if value.count('~') == 1:
            value, description = value.split('~')
        else:
            description = description

        value = value.strip()  # clean field
        original_value = value

        if len(value) > Attribute.VALUE_LEN:
            value = value[:Attribute.VALUE_LEN]

        queryset = Attribute.objects.filter(
            property_att=property_att, value=value
        )
        if queryset.exists():
            return queryset[0]

        if property_att.auto_add is False:
            raise ValidationError(
                _('The attribute cannot be created because'
                  ' property prevents it')
            )

        obj = Attribute()
        obj.property_att = property_att
        obj.value = value
        obj.description = description
        obj.save()

        if original_value != obj.value:
            Notification.objects.create(
                _('The value of the attribute [%s] has more than %d characters. '
                  'The original value is truncated: %s') % (
                    '<a href="{}">{}</a>'.format(
                        reverse('admin:server_attribute_change', args=(obj.id,)),
                        obj
                    ),
                    Attribute.VALUE_LEN,
                    original_value
                )
            )

        return obj


@python_2_unicode_compatible
class Attribute(models.Model, MigasLink):
    VALUE_LEN = 250

    property_att = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        verbose_name=_("Property")
    )

    value = models.CharField(
        verbose_name=_("value"),
        max_length=VALUE_LEN
    )

    description = models.TextField(
        verbose_name=_("description"),
        null=True,
        blank=True
    )

    _exclude_links = ["computer - tags"]

    objects = AttributeManager()

    TOTAL_COMPUTER_QUERY = "SELECT DISTINCT COUNT(server_computer.id) \
        FROM server_computer, server_computer_sync_attributes \
        WHERE server_attribute.id=server_computer_sync_attributes.attribute_id \
        AND server_computer_sync_attributes.computer_id=server_computer.id"

    def __str__(self):
        if self.id == 1:  # special case (SET-ALL SYSTEMS)
            return self.value
        elif self.property_att.prefix == 'CID' and \
                settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0] != 'id':
            return u'{} (CID-{})'.format(self.description, self.value)
        else:
            return u'{}-{}'.format(self.property_att.prefix, self.value)

    def total_computers(self, user=None):
        from . import Computer

        if user and not user.userprofile.is_view_all():
            queryset = Computer.productive.scope(user.userprofile).filter(sync_attributes__id=self.id)
        else:
            queryset = Computer.productive.filter(sync_attributes__id=self.id)

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

        if property_att.kind == "R" or property_att.kind == "L":
            if property_att.sort == 'server':
                obj = Attribute.objects.create(property_att, '')
                attributes.append(obj.id)

            lst = value.split(".")
            pos = 0

            if property_att.kind == "R":  # Adds right
                for item in lst:
                    obj = Attribute.objects.create(property_att, value[pos:])
                    attributes.append(obj.id)
                    pos += len(item) + 1

            if property_att.kind == "L":  # Adds left
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


class ServerAttributeManager(DomainAttributeManager):
    def scope(self, user):
        qs = super(ServerAttributeManager, self).scope(user)
        return qs.filter(property_att__sort='server')


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


class ClientAttributeManager(DomainAttributeManager):
    def scope(self, user):
        qs = super(ClientAttributeManager, self).scope(user)
        return qs.filter(
            Q(property_att__sort='client') |
            Q(property_att__sort='basic')
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


class BasicAttributeManager(DomainAttributeManager):
    def scope(self, user):
        qs = super(BasicAttributeManager, self).scope(user)
        return qs.filter(property_att__sort='basic')


class BasicAttribute(Attribute):
    objects = BasicAttributeManager()

    @staticmethod
    def process(**kwargs):
        properties = dict(Property.objects.filter(
            enabled=True, sort='basic'
        ).values_list('prefix', 'id'))

        basic_attributes = []

        if 'SET' in properties.keys():
            obj, _ = Attribute.objects.get_or_create(
                property_att=Property.objects.get(pk=properties['SET']),
                value='ALL SYSTEMS'  # FIXME 'All Systems'
            )
            basic_attributes.append(obj.id)

        if 'CID' in properties.keys() and 'id' in kwargs:
            description = u'{}'.format(kwargs['description'])
            obj, _ = Attribute.objects.get_or_create(
                property_att=Property.objects.get(pk=properties['CID']),
                value=str(kwargs['id']),
                defaults={'description': description}
            )
            obj.update_description(description)
            basic_attributes.append(obj.id)

        if 'PLT' in properties.keys() and 'platform' in kwargs:
            obj, _ = Attribute.objects.get_or_create(
                property_att=Property.objects.get(pk=properties['PLT']),
                value=kwargs['platform']
            )
            basic_attributes.append(obj.id)

        if 'IP' in properties.keys() and 'ip_address' in kwargs:
            obj, _ = Attribute.objects.get_or_create(
                property_att=Property.objects.get(pk=properties['IP']),
                value=kwargs['ip_address']
            )
            basic_attributes.append(obj.id)

        if 'PRJ' in properties.keys() and 'project' in kwargs:
            obj, _ = Attribute.objects.get_or_create(
                property_att=Property.objects.get(pk=properties['PRJ']),
                value=kwargs['project']
            )
            basic_attributes.append(obj.id)

        if 'USR' in properties.keys() and 'user' in kwargs:
            obj, _ = Attribute.objects.get_or_create(
                property_att=Property.objects.get(pk=properties['USR']),
                value=kwargs['user']
            )
            basic_attributes.append(obj.id)

        return basic_attributes

    class Meta:
        verbose_name = _("Basic Attribute")
        verbose_name_plural = _("Basic Attributes")
        proxy = True
