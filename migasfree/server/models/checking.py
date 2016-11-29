# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class Checking(models.Model):
    """
    For each register of this model, migasfree will show in the section Status
    of main menu the result of this 'checking'.
    The system only will show the checking if 'result' != 0
    """
    name = models.CharField(
        verbose_name=_("name"),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    description = models.TextField(
        verbose_name=_("description"),
        null=True,
        blank=True,
    )

    code = models.TextField(
        verbose_name=_("code"),
        blank=True,
        help_text=_("Django code. <br><b>VARIABLES TO SETTINGS:</b><br>"
                    "<b>result</b>: a number. "
                    "If result<>0 the checking is show in the section Status. "
                    "Default is 0<br>"
                    "<b>alert</b>: type of alert. Default is 'info'. "
                    "Enumeration value: {'info' | 'warning' | 'danger'}<br>"
                    "<b>url</b>: link. Default is '/'<br>"
                    "<b>msg</b>: The text to show. Default is the field name.<br>"
                    "<b>target</b>: Enumeration value: {'computer' | 'server'}")
    )

    active = models.BooleanField(
        verbose_name=_("active"),
        default=True,
    )

    def save(self, *args, **kwargs):
        self.code = self.code.replace("\r\n", "\n")
        super(Checking, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Checking")
        verbose_name_plural = _("Checkings")
        permissions = (("can_save_checking", "Can save Checking"),)
