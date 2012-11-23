# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models.common import link
from migasfree.server.models import Schedule, Attribute


class ScheduleDelay(models.Model):
    delay = models.IntegerField(unicode(_("delay")))

    schedule = models.ForeignKey(
        Schedule,
        verbose_name=unicode(_("schedule"))
    )

    attributes = models.ManyToManyField(
        Attribute,
        null=True,
        blank=True,
        verbose_name=unicode(_("attributes"))
    )

    def __unicode__(self):
        # return u'%s - %s' % (str(self.delay), self.schedule.name)
        return u''

    def list_attributes(self):
        cattributes = ""
        for i in self.attributes.all():
            cattributes = cattributes + i.value + ","

        return cattributes[0:len(cattributes) - 1]

    list_attributes.short_description = unicode(_("attributes"))

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Schedule Delay"))
        verbose_name_plural = unicode(_("Schedule Delays"))
        unique_together = (("schedule", "delay"),)
        permissions = (("can_save_scheduledelay", "Can save Schedule Delay"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
