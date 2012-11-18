# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from common import link
from server.models.computer_login_update_hwnode import Computer
from server.models.version import Version

from server.models.autocheck_error import AutoCheckError


class Error(models.Model):
    computer = models.ForeignKey(
        Computer,
        verbose_name=unicode(_("computer"))
    )

    date = models.DateTimeField(
        unicode(_("date")),
        default=0
    )

    error = models.TextField(
        unicode(_("error")),
        null=True,
        blank=True
    )

    checked = models.BooleanField(
        unicode(_("checked")),
        default=False,
        help_text=""
    )

    version = models.ForeignKey(
        Version,
        verbose_name=unicode(_("version"))
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
    computer_link.short_description = unicode(_("Computer"))

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
        verbose_name = unicode(_("Error"))
        verbose_name_plural = unicode(_("Errors"))
        permissions = (("can_save_error", "Can save Error"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
