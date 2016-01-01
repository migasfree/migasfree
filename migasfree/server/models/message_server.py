# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class MessageServer(models.Model):
    text = models.TextField(
        verbose_name=_("text"),
        null=True,
        blank=True
    )

    date = models.DateTimeField(
        verbose_name=_("date"),
        default=0
    )

    def __str__(self):
        return self.text

    class Meta:
        app_label = 'server'
        verbose_name = _("Message Server")
        verbose_name_plural = _("Messages Server")
        permissions = (("can_save_messageserver", "Can save Message Server"),)
