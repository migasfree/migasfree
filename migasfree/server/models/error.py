# -*- coding: utf-8 -*-

import re

from django.db import models
from django.utils import timezone, dateformat
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

    def truncated_error(self):
        if len(self.error) <= 250:
            return self.error
        else:
            return self.error[:250] + " ..."

    truncated_error.short_description = _("Truncated error")

    def auto_check(self):
        for ace in AutoCheckError.objects.all():
            if re.search(ace.message, self.error):
                self.checked =True
                return

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = _("Computer")

    def save(self, *args, **kwargs):
        self.error = self.error.replace("\r\n", "\n")
        self.auto_check()
        super(Error, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s (%s)' % (self.computer.__str__(), self.date)

    class Meta:
        app_label = 'server'
        verbose_name = _("Error")
        verbose_name_plural = _("Errors")
        permissions = (("can_save_error", "Can save Error"),)
