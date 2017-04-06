# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import Computer


class MessageManager(models.Manager):
    def create(self, computer, text):
        obj = Message()
        obj.computer = computer
        obj.text = text
        obj.save()

        return obj


@python_2_unicode_compatible
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

    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('date'))

    objects = MessageManager()

    def update_message(self, text):
        self.text = text
        self.save()

    def __str__(self):
        return u'{} ({:%Y-%m-%d %H:%M:%S})'.format(self.computer, self.updated_at)

    class Meta:
        app_label = 'server'
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        permissions = (("can_save_message", "Can save Message"),)
