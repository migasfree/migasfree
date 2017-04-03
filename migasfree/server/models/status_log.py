# -*- coding: utf-8 *-*

from django.db import models
from django.utils.translation import ugettext_lazy as _

from .computer import Computer
from .event import Event


class StatusLogManager(models.Manager):
    def create(self, computer):
        obj = StatusLog()
        obj.computer = computer
        obj.status = computer.status
        obj.save()

        return obj


class StatusLog(Event):
    status = models.CharField(
        verbose_name=_('status'),
        max_length=20,
        null=False,
        choices=Computer.STATUS_CHOICES,
        default='intended'
    )

    objects = StatusLogManager()

    class Meta:
        app_label = 'server'
        verbose_name = _("Status Log")
        verbose_name_plural = _("Status Logs")
        permissions = (("can_save_statuslog", "Can save Status Log"),)
