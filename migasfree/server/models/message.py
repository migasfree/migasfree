# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models import Computer


class Message(models.Model):
    computer = models.ForeignKey(
        Computer,
        verbose_name=_("computer"),
        unique=True
    )

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
        return u'%s - %s' % (self.computer.__unicode__(), self.text)

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = _("Computer")

    class Meta:
        app_label = 'server'
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        permissions = (("can_save_message", "Can save Message"),)
