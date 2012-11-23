# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models.common import link
from migasfree.server.models import Computer, FaultDef, Version


class Fault(models.Model):
    computer = models.ForeignKey(
        Computer,
        verbose_name=unicode(_("computer"))
    )

    faultdef = models.ForeignKey(
        FaultDef,
        verbose_name=unicode(_("fault definition"))
    )

    date = models.DateTimeField(
        unicode(_("date")),
        default=0
    )

    text = models.TextField(
        unicode(_("text")),
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

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = unicode(_("Computer"))

    def __unicode__(self):
        return u'%s - %s - %s' % (
            str(self.id),
            self.computer.name,
            str(self.date)
        )

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Fault"))
        verbose_name_plural = unicode(_("Faults"))
        permissions = (("can_save_fault", "Can save Fault"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
