# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from common import link


class Checking(models.Model):
    """
    For each register of this model, migasfree will show in the section Status
    of main menu the result of this 'checking'.
    The system only will show the checking if 'result' != 0
    """
    name = models.CharField(
        _("name"),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    description = models.TextField(
        _("description"),
        null=True,
        blank=True,
    )

    code = models.TextField(
        _("code"),
        null=False,
        blank=True,
        help_text=_("Code django. <br><b>VARIABLES TO SETTINGS:</b><br><b>result</b>: a number. If result<>0 the checking is show in the section Status. Default is 0<br><b>icon</b>: name of icon to show localizate in '/repo/icons'. Default is 'information.png'<br><b>url</b>: link. Default is '/migasfree/main'<br><b>msg</b>: The text to show. Default is the field name.")
    )

    active = models.BooleanField(
        _("active"),
        default=True,
    )

    alert = models.BooleanField(
        _("alert"),
        default=True,
    )

    def save(self, *args, **kwargs):
        self.code = self.code.replace("\r\n", "\n")
        super(Checking, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Checking")
        verbose_name_plural = _("Checkings")
        permissions = (("can_save_checking", "Can save Checking"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
