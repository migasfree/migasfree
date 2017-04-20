# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import Project, MigasLink
from .event import Event
from .user import User


class SynchronizationManager(models.Manager):
    def create(self, computer):
        obj = Synchronization()
        obj.computer = computer
        obj.project = computer.project
        obj.user = computer.sync_user
        obj.save()

        return obj


class Synchronization(Event, MigasLink):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("user")
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name=_("project"),
        null=True
    )

    objects = SynchronizationManager()

    def save(self, *args, **kwargs):
        super(Synchronization, self).save(*args, **kwargs)

        self.computer.sync_end_date = self.created_at
        self.computer.save()

    class Meta:
        app_label = 'server'
        verbose_name = _("Synchronization")
        verbose_name_plural = _("Synchronizations")
        permissions = (("can_save_synchronization", "Can save Synchronization"),)
