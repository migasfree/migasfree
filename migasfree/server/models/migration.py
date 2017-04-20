# -*- coding: utf-8 *-*

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import Project
from .event import Event


class MigrationManager(models.Manager):
    def create(self, computer, project):
        obj = Migration()
        obj.computer = computer
        obj.project = project
        obj.save()

        return obj


@python_2_unicode_compatible
class Migration(Event):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name=_("project")
    )

    objects = MigrationManager()

    def __str__(self):
        return u'{} ({:%Y-%m-%d %H:%M:%S}) {}'.format(
            self.computer, self.created_at, self.project
        )

    class Meta:
        app_label = 'server'
        verbose_name = _("Migration")
        verbose_name_plural = _("Migrations")
        permissions = (("can_save_migration", "Can save Migration"),)
