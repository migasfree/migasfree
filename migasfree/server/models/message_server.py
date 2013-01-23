# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from common import link


class MessageServer(models.Model):
    text = models.TextField(
        _("text"),
        null=True,
        blank=True
    )

    date = models.DateTimeField(
        _("date"),
        default=0
    )

    def __unicode__(self):
        return self.text

    class Meta:
        app_label = 'server'
        verbose_name = _("Message Server")
        verbose_name_plural = _("Messages Server")
        permissions = (("can_save_messageserver", "Can save Message Server"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
