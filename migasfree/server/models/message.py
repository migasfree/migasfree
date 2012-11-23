# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models.common import link
from migasfree.server.models import Computer


class Message(models.Model):
    computer = models.ForeignKey(
        Computer,
        verbose_name=unicode(_("computer")),
        unique=True
    )

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
        return u'%s - %s' % (self.computer.name, self.text)

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = unicode(_("Computer"))

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Message"))
        verbose_name_plural = unicode(_("Messages"))
        permissions = (("can_save_message", "Can save Message"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
