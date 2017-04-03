# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import FaultDef, Version
from .event import Event


class UncheckedManager(models.Manager):
    def get_queryset(self):
        return super(UncheckedManager, self).get_queryset().filter(
            checked=0
        )


class FaultManager(models.Manager):
    def create(self, computer, definition, result):
        obj = Fault()
        obj.computer = computer
        obj.version = computer.version
        obj.fault_definition = definition
        obj.result = result
        obj.save()

        return obj


class Fault(Event):
    fault_definition = models.ForeignKey(
        FaultDef,
        verbose_name=_("fault definition")
    )

    result = models.TextField(
        verbose_name=_("result"),
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
    unchecked = UncheckedManager()

    @staticmethod
    def unchecked_count():
        return Fault.objects.filter(checked=0).count()

    def checked_ok(self):
        self.checked = True
        self.save()

    def list_users(self):
        return self.fault_definition.list_users()

    class Meta:
        app_label = 'server'
        verbose_name = _("Fault")
        verbose_name_plural = _("Faults")
        permissions = (("can_save_fault", "Can save Fault"),)
