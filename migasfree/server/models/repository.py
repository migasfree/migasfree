# -*- coding: utf-8 -*-

import os
import datetime
import shutil

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from ..functions import horizon

from . import (
    Version,
    Package,
    Attribute,
    Schedule,
    MigasLink
)


class RepositoryManager(models.Manager):
    def by_version(self, version_id):
        return self.get_queryset().filter(version__id=version_id)


@python_2_unicode_compatible
class Repository(models.Model, MigasLink):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=50
    )

    version = models.ForeignKey(
        Version,
        verbose_name=_("version")
    )

    packages = models.ManyToManyField(
        Package,
        blank=True,
        verbose_name=_("Packages/Set"),
        help_text=_("Assigned Packages")
    )

    attributes = models.ManyToManyField(
        Attribute,
        blank=True,
        verbose_name=_("attributes"),
        help_text=_("Assigned Attributes")
    )

    excludes = models.ManyToManyField(
        Attribute,
        related_name="ExcludeAttribute",
        blank=True,
        verbose_name=_("excludes"),
        help_text=_("Excluded Attributes")
    )

    schedule = models.ForeignKey(
        Schedule,
        null=True,
        blank=True,
        verbose_name=_("schedule")
    )

    active = models.BooleanField(
        verbose_name=_("active"),
        default=True,
        help_text=_("if you uncheck this field, the repository is hidden for"
                    " all computers.")
    )

    date = models.DateField(
        verbose_name=_("date"),
        help_text=_("Date initial for distribute.")
    )

    comment = models.TextField(
        verbose_name=_("comment"),
        null=True,
        blank=True
    )

    toinstall = models.TextField(
        verbose_name=_("packages to install"),
        null=True,
        blank=True
    )

    toremove = models.TextField(
        verbose_name=_("packages to remove"),
        null=True,
        blank=True
    )

    defaultpreinclude = models.TextField(
        verbose_name=_("default preinclude packages"),
        null=True,
        blank=True
    )

    defaultinclude = models.TextField(
        verbose_name=_("default include packages"),
        null=True,
        blank=True
    )

    defaultexclude = models.TextField(
        verbose_name=_("default exclude packages"),
        null=True,
        blank=True
    )

    objects = RepositoryManager()

    def packages_link(self):
        return ' '.join([pkg.link() for pkg in self.packages.all()])

    packages_link.allow_tags = True
    packages_link.short_description = _("Packages")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)

        # TODO Remove this condition and assign default value in toinstall field
        if self.toinstall:
            self.toinstall = self.toinstall.replace("\r\n", "\n")

        # TODO Remove this condition and assign default value in toremove field
        if self.toremove:
            self.toremove = self.toremove.replace("\r\n", "\n")

        super(Repository, self).save(*args, **kwargs)

    @staticmethod
    def available_repos(computer, attributes):
        """
        Return available repositories for a computer and attributes list
        """
        # 1.- all repositories by attribute
        attributed = Repository.objects.filter(
            active=True
        ).filter(
            version__id=computer.version.id
        ).filter(
            attributes__id__in=attributes
        ).filter(
            date__lte=datetime.datetime.now().date()
        ).values_list('id', flat=True)
        lst = list(attributed)

        # 2.- Add to "dic_repos" all repositories by schedule
        scheduled = Repository.objects.filter(
            active=True
        ).filter(
            version__id=computer.version.id
        ).filter(
            schedule__scheduledelay__attributes__id__in=attributes
        ).extra(
            select={
                "delay": "server_scheduledelay.delay",
                "duration": "server_scheduledelay.duration"
            }
        )

        for r in scheduled:
            for duration in range(0, r.duration):
                if computer.id % r.duration == duration:
                    if horizon(
                        r.date, r.delay + duration
                    ) <= datetime.datetime.now().date():
                        lst.append(r.id)
                        break

        # 3.- excluded attributes
        repositories = Repository.objects.filter(
            id__in=lst
        ).filter(
            ~models.Q(excludes__id__in=attributes)
        ).order_by('name')

        return repositories

    def path(self, name=None):
        return os.path.join(
            Version.path(self.version.name),
            self.version.pms.slug,
            name
        )

    class Meta:
        app_label = 'server'
        verbose_name = _("Repository")
        verbose_name_plural = _("Repositories")
        unique_together = (("name", "version"),)
        permissions = (("can_save_repository", "Can save Repository"),)
        ordering = ['version__name', 'name']


@receiver(pre_delete, sender=Repository)
def pre_delete_deployment(sender, instance, **kwargs):
    path = instance.path()
    if os.path.exists(path):
        shutil.rmtree(path)
