# -*- coding: utf-8 *-*
from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models.common import link
from migasfree.server.models import Computer
from migasfree.server.models import Version


class Migration(models.Model):
    computer = models.ForeignKey(
        Computer,
        verbose_name=_("computer"),
    )

    version = models.ForeignKey(
        Version,
        verbose_name=_("version")
    )

    date = models.DateTimeField(
        _("date"),
        default=0
    )

    def __unicode__(self):
        return u'%s - %s' % (self.computer.name, self.version)

    def computer_link(self):
        return self.computer.link()
    computer_link.allow_tags = True
    computer_link.short_description = _("Computer")

    def version_link(self):
        return self.version.link()
    version_link.allow_tags = True
    version_link.short_description = _("Version")

    class Meta:
        app_label = 'server'
        verbose_name = _("Migration")
        verbose_name_plural = _("Migrations")
        permissions = (("can_save_migration", "Can save Migration"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
