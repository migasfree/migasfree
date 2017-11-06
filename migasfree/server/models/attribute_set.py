# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from . import (
    Property,
    Attribute,
    MigasLink
)


@python_2_unicode_compatible
class AttributeSet(models.Model, MigasLink):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=50,
        unique=True
    )

    description = models.TextField(
        verbose_name=_("description"),
        null=True,
        blank=True
    )

    enabled = models.BooleanField(
        verbose_name=_("enabled"),
        default=True,
    )

    included_attributes = models.ManyToManyField(
        Attribute,
        blank=True,
        verbose_name=_("included attributes"),
    )

    excluded_attributes = models.ManyToManyField(
        Attribute,
        related_name="ExcludedAttributesGroup",
        blank=True,
        verbose_name=_("excluded attributes"),
    )

    def __str__(self):
        return self.name

    def clean(self):
        super(AttributeSet, self).clean()

        if self.id:
            att_set = AttributeSet.objects.get(pk=self.id)
            if att_set.name != self.name and \
                    Attribute.objects.filter(
                        property_att=Property.objects.get(prefix='SET', sort='basic'),
                        value=self.name
                    ).count() > 0:
                raise ValidationError(_('Duplicated name'))

    def save(self, *args, **kwargs):
        super(AttributeSet, self).save(*args, **kwargs)

        Attribute.objects.get_or_create(
            property_att=Property.objects.get(prefix='SET', sort='basic'),
            value=self.name,
            defaults={'description': ''}
        )

    @staticmethod
    def item_at_index(lst, item, before=-1):
        try:
            id_before = lst.index(before)
        except ValueError:
            id_before = -1

        try:
            id_item = lst.index(item)
        except ValueError:
            id_item = -1

        if id_item == -1:
            if id_before == -1:
                lst.append(item)
            else:
                lst.insert(id_before, item)
        else:
            if id_before > -1:
                if id_before < id_item:
                    lst = lst[0:id_before] + lst[id_item:] \
                        + lst[id_before:id_item]

        return lst

    @staticmethod
    def get_sets():
        sets = []
        for item in AttributeSet.objects.filter(enabled=True):
            sets = AttributeSet.item_at_index(sets, item.id)

            for subset in item.included_attributes.filter(
                ~Q(property_att__sort='basic')
            ).filter(property_att__prefix='SET').filter(~Q(value=item.name)):
                sets = AttributeSet.item_at_index(
                    sets,
                    AttributeSet.objects.get(name=subset.value).id,
                    before=item.id
                )

            for subset in item.excluded_attributes.filter(
                ~Q(property_att__sort='basic')
            ).filter(property_att__prefix='SET').filter(~Q(value=item.name)):
                sets = AttributeSet.item_at_index(
                    sets,
                    AttributeSet.objects.get(name=subset.value).id,
                    before=item.id
                )

        return sets

    @staticmethod
    def process(attributes):
        property_set = Property.objects.get(prefix='SET', sort='basic')

        att_id = []
        for item in AttributeSet.get_sets():
            for att_set in AttributeSet.objects.filter(id=item).filter(
                Q(included_attributes__id__in=attributes)
            ).filter(~Q(excluded_attributes__id__in=attributes)):
                att = Attribute.objects.create(property_set, att_set.name)
                att_id.append(att.id)

        return att_id

    class Meta:
        app_label = 'server'
        verbose_name = _("Attribute Set")
        verbose_name_plural = _("Attribute Sets")
        permissions = (("can_save_attributeset", "Can save Attribute Sets"),)


@receiver(pre_save, sender=AttributeSet)
def pre_save_attribute_set(sender, instance, **kwargs):
    if instance.id:
        att_set = AttributeSet.objects.get(pk=instance.id)
        if instance.name != att_set.name:
            att = Attribute.objects.get(
                property_att=Property.objects.get(prefix='SET', sort='basic'),
                value=att_set.name
            )
            att.update_value(instance.name)


@receiver(pre_delete, sender=AttributeSet)
def pre_delete_attribute_set(sender, instance, **kwargs):
    Attribute.objects.filter(
        property_att=Property.objects.get(prefix='SET', sort='basic'),
        value=instance.name
    ).delete()
