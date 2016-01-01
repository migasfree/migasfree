# -*- coding: utf-8 *-*

from django.db import models
from django.utils import timezone, dateformat
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import Computer, Version


class MigrationManager(models.Manager):
    def create(self, computer, version):
        obj = Migration()
        obj.computer = computer
        obj.version = version
        obj.date = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        obj.save()

        return obj


@python_2_unicode_compatible
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
        verbose_name=_("date"),
        default=0
    )

    objects = MigrationManager()

    def __str__(self):
        return '%s (%s) %s' % (self.computer, self.date, self.version)

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
