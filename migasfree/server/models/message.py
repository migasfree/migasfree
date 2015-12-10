# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone, dateformat

from . import Computer


class MessageManager(models.Manager):
    def create(self, computer, text):
        obj = Message()
        obj.computer = computer
        obj.text = text
        obj.date = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        obj.save()

        return obj


class Message(models.Model):
    computer = models.OneToOneField(
        Computer,
        on_delete=models.CASCADE,
        verbose_name=_("computer"),
    )

    text = models.TextField(
        verbose_name=_("text"),
        null=True,
        blank=True
    )

    date = models.DateTimeField(
        verbose_name=_("date"),
        default=0
    )

    objects = MessageManager()

    def update_message(self, text):
        self.text = text
        self.date = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        self.save()

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
