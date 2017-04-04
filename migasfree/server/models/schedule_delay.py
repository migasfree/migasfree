# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Count
from django.core.validators import MinValueValidator
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import Schedule, Attribute, Computer, UserProfile


@python_2_unicode_compatible
class ScheduleDelay(models.Model):
    delay = models.IntegerField(
        verbose_name=_("delay")
    )

    schedule = models.ForeignKey(
        Schedule,
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

    def total_computers(self):
        queryset = Computer.objects.filter(
            sync_attributes__id__in=self.attributes.all().values_list('id')
        )

        version = UserProfile.get_logged_version()
        if version:
            queryset = queryset.filter(version_id=version.id)

        return queryset.annotate(total=Count('id')).order_by('id').count()

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
