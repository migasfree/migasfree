# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.aggregates import Count
from django.utils import timezone, dateformat
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import Computer, FaultDef, Version


class FaultManager(models.Manager):
    def create(self, computer, version, faultdef, text):
        obj = Fault()
        obj.computer = computer
        obj.version = version
        obj.faultdef = faultdef
        obj.text = text
        obj.date = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        obj.save()

        return obj


@python_2_unicode_compatible
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
        default=0
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

    def okay(self):
        self.checked = True
        self.save()

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = _("Computer")

    def list_users(self):
        return self.faultdef.list_users()

    @staticmethod
    def by_day(computer_id, start_date, end_date):
        return Fault.objects.filter(
            computer__id=computer_id,
            date__range=(start_date, end_date)
        ).extra(
            {"day": "date_trunc('day', date)"}
        ).values("day").annotate(count=Count("id")).order_by('-day')

    def __str__(self):
        return '%s (%s)' % (self.computer, self.date)

    class Meta:
        app_label = 'server'
        verbose_name = _("Fault")
        verbose_name_plural = _("Faults")
        permissions = (("can_save_fault", "Can save Fault"),)
