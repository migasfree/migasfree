# -*- coding: utf-8 -*-

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_delete
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

    def __str__(self):
        return self.name

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
        for item in AttributeSet.objects.filter(active=True):
            sets = AttributeSet.item_at_index(sets, item.id)

            for subset in item.attributes.filter(
                id__gt=1
            ).filter(
                property_att__id=1
            ).filter(~models.Q(value=item.name)):
                sets = AttributeSet.item_at_index(
                    sets,
                    AttributeSet.objects.get(name=subset.value).id,
                    before=item.id
                )

            for subset in item.excludes.filter(
                id__gt=1
            ).filter(
                property_att__id=1
            ).filter(~models.Q(value=item.name)):
                sets = AttributeSet.item_at_index(
                    sets,
                    AttributeSet.objects.get(name=subset.value).id,
                    before=item.id
                )

        return sets

    @staticmethod
    def process(attributes):
        property_set = Property.objects.get(id=1)

        att_id = []
        for item in AttributeSet.get_sets():
            for soa in AttributeSet.objects.filter(id=item).filter(
                models.Q(attributes__id__in=attributes)
            ).filter(~models.Q(excludes__id__in=attributes)):
                att = Attribute.objects.create(property_set, soa.name)
                att_id.append(att.id)
                attributes.append(att.id)

        return att_id

    class Meta:
        app_label = 'server'
        verbose_name = _("Attributes Set")
        verbose_name_plural = _("Attributes Sets")
        permissions = (("can_save_attributteset", "Can save Attributes Set"),)


@receiver(pre_delete, sender=AttributeSet)
def pre_delete_set_of_attributes(sender, instance, **kwargs):
    try:
        Attribute.objects.get(property_att=Property(id=1), value=instance.name).delete()
    except ObjectDoesNotExist:
        pass
