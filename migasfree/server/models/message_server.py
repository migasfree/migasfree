# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from common import link


class MessageServer(models.Model):
    text = models.CharField(
        unicode(_("text")),
        max_length=100,
        null=True,
        blank=True
    )

    date = models.DateTimeField(
        unicode(_("date")),
        default=0
    )

    def __unicode__(self):
        return u'%s' % (self.text)

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Message Server"))
        verbose_name_plural = unicode(_("Messages Server"))
        permissions = (("can_save_messageserver", "Can save Message Server"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
