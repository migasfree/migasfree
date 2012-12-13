# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models.common import link
from migasfree.server.models import Computer, Version, AutoCheckError


class Error(models.Model):
    computer = models.ForeignKey(
        Computer,
        verbose_name=_("computer")
    )

    date = models.DateTimeField(
        _("date"),
        default=0
    )

    error = models.TextField(
        _("error"),
        null=True,
        blank=True
    )

    checked = models.BooleanField(
        _("checked"),
        default=False,
    )

    version = models.ForeignKey(
        Version,
        verbose_name=_("version")
    )

    def auto_check(self):
        msg = self.error
        for ace in AutoCheckError.objects.all():
            msg = msg.replace(ace.message, "")

        msg = msg.replace("\n", "")
        if msg == "":
            self.checked = True

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = _("Computer")

    def save(self, *args, **kwargs):
        self.error = self.error.replace("\r\n", "\n")
        self.auto_check()
        super(Error, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s - %s - %s' % (
            str(self.id),
            self.computer.name,
            str(self.date)
        )

    class Meta:
        app_label = 'server'
        verbose_name = _("Error")
        verbose_name_plural = _("Errors")
        permissions = (("can_save_error", "Can save Error"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
