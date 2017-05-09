# -*- coding: utf-8 -*-

import os
import shutil
import datetime

from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from ..utils import time_horizon

from . import (
    Project,
    Package,
    Attribute,
    Schedule,
    ScheduleDelay,
    MigasLink
)


class DeploymentManager(models.Manager):
    def by_project(self, project_id):
        return self.get_queryset().filter(project__id=project_id)


@python_2_unicode_compatible
class Deployment(models.Model, MigasLink):
    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=True,
        help_text=_("if you uncheck this field, deployment is disabled for all"
                    " computers.")
    )

    name = models.CharField(
        max_length=50,
        verbose_name=_('name')
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name=_("project")
    )

    comment = models.TextField(
        verbose_name=_("comment"),
        null=True,
        blank=True
    )

    available_packages = models.ManyToManyField(
        Package,
        blank=True,
        verbose_name=_('available packages'),
        help_text=_('If a computer has installed one of these packages it will'
                    ' be updated')
    )

    packages_to_install = models.TextField(
        verbose_name=_("packages to install"),
        null=True,
        blank=True,
        help_text=_('Mandatory packages to install each time')
    )

    packages_to_remove = models.TextField(
        verbose_name=_("packages to remove"),
        null=True,
        blank=True,
        help_text=_('Mandatory packages to remove each time')
    )

    included_attributes = models.ManyToManyField(
        Attribute,
        blank=True,
        verbose_name=_("included attributes")
    )

    excluded_attributes = models.ManyToManyField(
        Attribute,
        related_name="ExcludeAttribute",
        blank=True,
        verbose_name=_("excluded attributes")
    )

    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        verbose_name=_('schedule'),
        null=True,
        blank=True
    )

    start_date = models.DateField(
        default=timezone.now,
        verbose_name=_('start date')
    )

    default_preincluded_packages = models.TextField(
        verbose_name=_("default pre-included packages"),
        null=True,
        blank=True
    )

    default_included_packages = models.TextField(
        verbose_name=_("default included packages"),
        null=True,
        blank=True
    )

    default_excluded_packages = models.TextField(
        verbose_name=_("default excluded packages"),
        null=True,
        blank=True
    )

    objects = DeploymentManager()

    def __str__(self):
        return self.name

    @staticmethod
    def get_percent(begin_date, end_date):
        delta = end_date - begin_date
        progress = datetime.datetime.now() - datetime.datetime.combine(
            begin_date, datetime.datetime.min.time()
        )

        if delta.days > 0:
            percent = float(progress.days) / delta.days * 100
            if percent > 100:
                percent = 100
        else:
            percent = 100

        return percent

    def schedule_timeline(self):
        if self.schedule is None:
            return None

        delays = ScheduleDelay.objects.filter(
            schedule__id=self.schedule.id
        ).order_by('delay')

        if len(delays) == 0:
            return None

        begin_date = time_horizon(self.start_date, delays[0].delay)
        end_date = time_horizon(
            self.start_date,
            delays.reverse()[0].delay + delays.reverse()[0].duration
        )

        return {
            'begin_date': str(begin_date),
            'end_date': str(end_date),
            'percent': '%d' % self.get_percent(begin_date, end_date)
        }

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)

        if self.packages_to_install:
            self.packages_to_install = self.packages_to_install.replace("\r\n", "\n")
        if self.packages_to_remove:
            self.packages_to_remove = self.packages_to_remove.replace("\r\n", "\n")

        if self.default_preincluded_packages:
            self.default_preincluded_packages = self.default_preincluded_packages.replace("\r\n", "\n")
        if self.default_included_packages:
            self.default_included_packages = self.default_included_packages.replace("\r\n", "\n")
        if self.default_excluded_packages:
            self.default_excluded_packages = self.default_excluded_packages.replace("\r\n", "\n")

        super(Deployment, self).save(*args, **kwargs)

    @staticmethod
    def available_deployments(computer, attributes):
        """
        Return available deployments for a computer and attributes list
        """
        # 1.- all deployments by attribute
        attributed = Deployment.objects.filter(
            project__id=computer.project.id,
            enabled=True,
            included_attributes__id__in=attributes,
            start_date__lte=datetime.datetime.now().date()
        ).values_list('id', flat=True)
        lst = list(attributed)

        # 2.- all deployments by schedule
        scheduled = Deployment.objects.filter(
            project__id=computer.project.id,
            enabled=True,
            schedule__delays__attributes__id__in=attributes
        ).extra(
            select={
                'delay': 'server_scheduledelay.delay',
                'duration': 'server_scheduledelay.duration'
            }
        )

        for deploy in scheduled:
            for duration in range(0, deploy.duration):
                if computer.id % deploy.duration == duration:
                    if time_horizon(
                        deploy.start_date, deploy.delay + duration
                    ) <= datetime.datetime.now().date():
                        lst.append(deploy.id)
                        break

        # 3.- excluded attributes
        deployments = Deployment.objects.filter(id__in=lst).filter(
            ~Q(excluded_attributes__id__in=attributes)
        ).order_by('name')

        return deployments

    def path(self, name=''):
        return os.path.join(
            Project.path(self.project.name),
            self.project.pms.slug,
            name
        )

    class Meta:
        app_label = 'server'
        verbose_name = _('Deployment')
        verbose_name_plural = _('Deployments')
        unique_together = (('name', 'project'),)
        permissions = (("can_save_deployment", "Can save Deployment"),)
        ordering = ['project__name', 'name']


@receiver(pre_save, sender=Deployment)
def pre_save_deployment(sender, instance, **kwargs):
    if instance.id:
        old_obj = Deployment.objects.get(pk=instance.id)
        if old_obj.project.id != instance.project.id:
            raise ValidationError(_('Is not allowed change project'))


@receiver(pre_delete, sender=Deployment)
def pre_delete_deployment(sender, instance, **kwargs):
    path = instance.path()
    if os.path.exists(path):
        shutil.rmtree(path)
