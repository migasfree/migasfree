# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import Computer, FaultDef, Version


class FaultManager(models.Manager):
    def create(self, computer, version, faultdef, text):
        fault = Fault()
        fault.computer = computer
        fault.version = version
        fault.faultdef = faultdef
        fault.text = text
        fault.save()

        return fault


class Fault(models.Model):
    computer = models.ForeignKey(
        Computer,
        verbose_name=_("computer")
    )

    faultdef = models.ForeignKey(
        FaultDef,
        verbose_name=_("fault definition")
    )

    date = models.DateTimeField(
        verbose_name=_("date"),
        auto_now_add=True
    )

    text = models.TextField(
        verbose_name=_("text"),
        null=True,
        blank=True
    )

    checked = models.BooleanField(
        verbose_name=_("checked"),
        default=False,
    )

    version = models.ForeignKey(
        Version,
        verbose_name=_("version")
    )

    objects = FaultManager()

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = _("Computer")

    def list_users(self):
        return self.faultdef.list_users()

    def __unicode__(self):
        return '%d - %s - %s' % (
            self.id,
            self.computer.__unicode__(),
            str(self.date)
        )

    class Meta:
        app_label = 'server'
        verbose_name = _("Fault")
        verbose_name_plural = _("Faults")
        permissions = (("can_save_fault", "Can save Fault"),)
