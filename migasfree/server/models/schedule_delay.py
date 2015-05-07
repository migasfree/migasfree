# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator
from django.db.models import Count

from migasfree.server.models import Schedule, Attribute, user_version
from migasfree.server.models import Login


class ScheduleDelay(models.Model):
    delay = models.IntegerField(_("delay"))

    schedule = models.ForeignKey(
        Schedule,
        verbose_name=_("schedule")
    )

    attributes = models.ManyToManyField(
        Attribute,
        null=True,
        blank=True,
        verbose_name=_("attributes")
    )

    duration = models.IntegerField(
        _("duration"),
        default=1,
        validators=[MinValueValidator(1), ]
    )

    def total_computers(self):
        version=user_version()
        if version:
            return Login.objects.filter(attributes__id__in=self.attributes.all().values_list("id"), computer__version_id=version.id).annotate(total=Count('id')).order_by('id').count()
        else:
            return Login.objects.filter(attributes__id__in=self.attributes.all().values_list("id")).annotate(total=Count('id')).order_by('id').count()

    def __unicode__(self):
        # return u'%s - %s' % (str(self.delay), self.schedule.name)
        return u''

    def list_attributes(self):
        cattributes = ""
        for i in self.attributes.all():
            cattributes = cattributes + i.value + ","

        return cattributes[0:len(cattributes) - 1]

    list_attributes.short_description = _("attributes")

    class Meta:
        app_label = 'server'
        verbose_name = _("Schedule Delay")
        verbose_name_plural = _("Schedule Delays")
        unique_together = (("schedule", "delay"),)
        permissions = (("can_save_scheduledelay", "Can save Schedule Delay"),)
