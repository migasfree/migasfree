# -*- coding: utf-8 -*-

import re

from django.db import models
from django.db.models.aggregates import Count
from django.utils import timezone, dateformat
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import Computer, Version, AutoCheckError


class ErrorManager(models.Manager):
    def create(self, computer, version, error):
        obj = Error()
        obj.computer = computer
        obj.version = version
        obj.error = error
        obj.date = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        obj.save()

        return obj


@python_2_unicode_compatible
class Error(models.Model):
    computer = models.ForeignKey(
        Computer,
        verbose_name=_("computer")
    )

    date = models.DateTimeField(
        verbose_name=_("date"),
        default=0
    )

    error = models.TextField(
        verbose_name=_("error"),
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

    objects = ErrorManager()

    def okay(self, *args, **kwargs):
        self.checked = True
        super(Error, self).save(*args, **kwargs)

    def auto_check(self):
        for ace in AutoCheckError.objects.all():
            if re.search(ace.message, self.error):
                self.checked = True
                return

    def save(self, *args, **kwargs):
        self.error = self.error.replace("\r\n", "\n")
        self.auto_check()
        super(Error, self).save(*args, **kwargs)

    @classmethod
    def by_day(cls, computer_id, start_date, end_date):
        return cls.objects.filter(
            computer__id=computer_id,
            date__range=(start_date, end_date)
        ).extra(
            {"day": "date_trunc('day', date)"}
        ).values("day").annotate(count=Count("id")).order_by('-day')

    def __str__(self):
        return '{} ({})'.format(self.computer, self.date)

    class Meta:
        app_label = 'server'
        verbose_name = _("Error")
        verbose_name_plural = _("Errors")
        permissions = (("can_save_error", "Can save Error"),)
