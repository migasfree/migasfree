# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from ..utils import list_difference

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
            prefix='DMN', sort='basic',
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

    def update_domain_admins(self, users):
        """
        :param users: [id1, id2, id3, ...]
        :return: void
        """
        from .userprofile import UserProfile

        initial_admins = list(self.userprofile_set.values_list('id', flat=True))

        for pk in list_difference(initial_admins, users):
            try:
                user = UserProfile.objects.get(pk=pk)
                user.domains.remove(self.id)
                if user.domain_preference == self.id:
                    user.update_domain(0)
                self.userprofile_set.remove(user)
            except UserProfile.DoesNotExist:
                pass

        for pk in list_difference(users, initial_admins):
            try:
                user = UserProfile.objects.get(pk=pk)
                user.domains.add(self.id)
                self.userprofile_set.add(user)
            except UserProfile.DoesNotExist:
                pass

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.name = slugify(self.name).upper()
        super(Domain, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        app_label = 'server'
        verbose_name = _("Domain")
        verbose_name_plural = _("Domains")
        permissions = (("can_save_domain", "Can save Domain"),)
