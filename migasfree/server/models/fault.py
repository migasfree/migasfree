# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import FaultDefinition, Project
from .event import Event


class DomainFaultManager(models.Manager):
    def scope(self, user):
        qs = super(DomainFaultManager, self).get_queryset()
        if not user.is_view_all():
            qs = qs.filter(
                project_id__in=user.get_projects(),
                computer_id__in=user.get_computers()
            )

        return qs


class UncheckedManager(DomainFaultManager):
    def get_queryset(self):
        return super(UncheckedManager, self).get_queryset().filter(
            checked=0
        )

    def scope(self, user):
        return super(UncheckedManager, self).scope(user).filter(
            checked=0
        ).filter(
            models.Q(fault_definition__users__id__in=[user.id, ])
            | models.Q(fault_definition__users=None)
        )


class FaultManager(DomainFaultManager):
    def create(self, computer, definition, result):
        obj = Fault()
        obj.computer = computer
        obj.project = computer.project
        obj.fault_definition = definition
        obj.result = result
        obj.save()

        return obj


class Fault(Event):
    USER_FILTER_CHOICES = (
        ('me', _('To check for me')),
        ('only_me', _('Assigned to me')),
        ('others', _('Assigned to others')),
        ('unassigned', _('Unassigned')),
    )

    fault_definition = models.ForeignKey(
        FaultDefinition,
        on_delete=models.CASCADE,
        verbose_name=_("fault definition")
    )

    result = models.TextField(
        verbose_name=_("result"),
        null=True,
        blank=True
    )

    checked = models.BooleanField(
        verbose_name=_("checked"),
        default=False,
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name=_("project")
    )

    objects = FaultManager()
    unchecked = UncheckedManager()

    @staticmethod
    def unchecked_count(user=None):
        queryset = Fault.unchecked.scope(user)
        if user:
            queryset = queryset.filter(
                models.Q(fault_definition__users__id__in=[user.id, ])
                | models.Q(fault_definition__users=None)
            )

        return queryset.count()

    def checked_ok(self):
        self.checked = True
        self.save()

    def list_users(self):
        return self.fault_definition.list_users()

    class Meta:
        app_label = 'server'
        verbose_name = _("Fault")
        verbose_name_plural = _("Faults")
        permissions = (("can_save_fault", "Can save Fault"),)
