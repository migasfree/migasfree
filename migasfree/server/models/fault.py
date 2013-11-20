# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models.common import link
from migasfree.server.models import Computer, FaultDef, Version


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
        _("date"),
        default=0
    )

    text = models.TextField(
        _("text"),
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

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = _("Computer")

    def __unicode__(self):
        return u'%s - %s - %s' % (
            str(self.id),
            self.computer.__unicode__(),
            str(self.date)
        )

    class Meta:
        app_label = 'server'
        verbose_name = _("Fault")
        verbose_name_plural = _("Faults")
        permissions = (("can_save_fault", "Can save Fault"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

    def list_users(self):
        return self.faultdef.list_users()
