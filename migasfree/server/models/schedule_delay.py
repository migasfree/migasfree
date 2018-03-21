# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.db.models import Count
from django.core.validators import MinValueValidator
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import Schedule, Attribute, Computer


class ScheduleDelayManager(models.Manager):
    def scope(self, user):
        qs = super(ScheduleDelayManager, self).get_queryset()
        if not user.is_view_all():
            qs = qs.filter(
                Q(attributes__in=user.get_attributes()) |
                Q(attributes__in=user.get_domain_tags())
            )
        return qs

@python_2_unicode_compatible
class ScheduleDelay(models.Model):
    delay = models.IntegerField(
        verbose_name=_("delay")
    )

    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='delays',
        verbose_name=_("schedule")
    )

    attributes = models.ManyToManyField(
        Attribute,
        blank=True,
        verbose_name=_("attributes")
    )

    duration = models.IntegerField(
        verbose_name=_("duration"),
        default=1,
        validators=[MinValueValidator(1), ]
    )

    objects = ScheduleDelayManager()

    TOTAL_COMPUTER_QUERY = "SELECT DISTINCT COUNT(server_computer.id) \
        FROM server_computer, server_computer_sync_attributes \
        WHERE server_scheduledelay_attributes.attribute_id=server_computer_sync_attributes.attribute_id \
        AND server_computer_sync_attributes.computer_id=server_computer.id \
        AND server_computer.status <> 'unsubscribed'"

    def total_computers(self, user=None):
        if user and not user.userprofile.is_view_all():
            queryset = Computer.productive.scope(user.userprofile).filter(
                sync_attributes__id__in=self.attributes.values_list('id')
            )
        else:
            queryset = Computer.productive.filter(
                sync_attributes__id__in=self.attributes.values_list('id')
            )
        return queryset.annotate(total=Count('id')).count()

    total_computers.short_description = _('Total computers')

    def __str__(self):
        return u'{} ({})'.format(self.schedule.name, self.delay)

    def attribute_list(self):
        return ', '.join(
            self.attributes.values_list('value', flat=True).order_by('value')
        )

    attribute_list.short_description = _("attribute list")

    class Meta:
        app_label = 'server'
        verbose_name = _("Schedule Delay")
        verbose_name_plural = _("Schedule Delays")
        unique_together = (("schedule", "delay"),)
        permissions = (("can_save_scheduledelay", "Can save Schedule Delay"),)
