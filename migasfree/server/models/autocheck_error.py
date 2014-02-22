# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class AutoCheckError(models.Model):
    """
    This model is used to autocheck the errors and marked as 'check' when they
    are introducing in the system (Sometimes the Package Management System, in
    the clients, return a string error when in reliaty it is only a warning)
    The origen of this problem is that the package is bad packed.
    """
    message = models.TextField(
        _("message"),
        null=True,
        blank=True,
        help_text=_("Text of error that is only a warning. You can copy/paste from the field 'error' of a Error.")
    )

    def save(self, *args, **kwargs):
        self.message = self.message.replace("\r\n", "\n")
        super(AutoCheckError, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.message

    class Meta:
        app_label = 'server'
        verbose_name = _("Auto Check Error")
        verbose_name_plural = _("Auto Check Errors")
        permissions = (("can_save_autocheckerror", "Can save Auto Check Error"),)
