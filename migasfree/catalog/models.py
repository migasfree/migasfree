# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from markdownx.models import MarkdownxField

from migasfree.server.models import Project, Attribute, MigasLink
from migasfree.server.utils import to_list

_UNSAVED_IMAGEFIELD = 'unsaved_imagefield'


class DomainPackagesByProjectManager(models.Manager):
    def scope(self, user):
        qs = super(DomainPackagesByProjectManager, self).get_queryset()
        if not user.is_view_all():
            qs = qs.filter(project__in=user.get_projects())

        return qs


class PackagesByProjectManager(DomainPackagesByProjectManager):
    def create(self, application, project, packages_to_install):
        obj = PackagesByProject()
        obj.application = application
        obj.project = project
        obj.packages_to_install = packages_to_install
        obj.save()

        return obj


class MediaFileSystemStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if max_length and len(name) > max_length:
            raise(Exception("name's length is greater than max_length"))

        return name

    def _save(self, name, content):
        if self.exists(name):
            os.remove(os.path.join(settings.MIGASFREE_PUBLIC_DIR, name))

        return super(MediaFileSystemStorage, self)._save(name, content)


def upload_path_handler(instance, filename):
    _, ext = os.path.splitext(filename)
    return 'catalog_icons/app_{}{}'.format(instance.pk, ext)


class Application(models.Model, MigasLink):
    LEVELS = (
        ('U', _('User')),
        ('A', _('Admin')),
    )

    CATEGORIES = (
        (1, _('Accessories')),
        (2, _('Books')),
        (3, _('Developers Tools')),
        (4, _('Education')),
        (5, _('Fonts')),
        (6, _('Games')),
        (7, _('Graphics')),
        (8, _('Internet')),
        (9, _('Medicine')),
        (10, _('Office')),
        (11, _('Science & Engineering')),
        (12, _('Sound & Video')),
        (13, _('Themes & Tweaks')),
        (14, _('Universal Access')),
    )

    name = models.CharField(
        verbose_name=_('name'),
        max_length=50,
        unique=True
    )

    description = MarkdownxField(
        verbose_name=_('description'),
        blank=True,
        help_text=_('markdown syntax allowed')
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('date'))

    score = models.IntegerField(
        verbose_name=_('score'),
        default=1,
        choices=((1, 1), (2, 2), (3, 3), (4, 4), (5, 5)),
        help_text=_('Relevance to the organization')
    )

    icon = models.ImageField(
        verbose_name=_('icon'),
        upload_to=upload_path_handler,
        storage=MediaFileSystemStorage(),
        null=True
    )

    level = models.CharField(
        verbose_name=_('level'),
        max_length=1,
        default='U',
        choices=LEVELS
    )

    category = models.IntegerField(
        verbose_name=_('category'),
        default=1,
        choices=CATEGORIES
    )

    available_for_attributes = models.ManyToManyField(
        Attribute,
        blank=True,
        verbose_name=_("available for attributes")
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'catalog'
        verbose_name = _('Application')
        verbose_name_plural = _('Applications')
        permissions = (('can_save_application', 'Can save application'),)


class PackagesByProject(models.Model, MigasLink):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        verbose_name=_('application'),
        related_name='packages_by_project'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name=_('project')
    )

    packages_to_install = models.TextField(
        verbose_name=_('packages to install'),
        blank=True,
    )

    objects = PackagesByProjectManager()

    def __str__(self):
        return '{}@{}'.format(self.application, self.project)

    class Meta:
        app_label = 'catalog'
        verbose_name = _('Packages by Project')
        verbose_name_plural = _('Packages by Projects')
        unique_together = (('application', 'project'),)
        permissions = (('can_save_packagesbyproject', 'Can save packages by project'),)


class Policy(models.Model, MigasLink):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=50
    )

    enabled = models.BooleanField(
        verbose_name=_("enabled"),
        default=True,
        help_text=_("if you uncheck this field, the policy is disabled for"
                    " all computers.")
    )

    exclusive = models.BooleanField(
        verbose_name=_('exclusive'),
        default=True,
    )

    comment = models.TextField(
        verbose_name=_("comment"),
        null=True,
        blank=True
    )

    included_attributes = models.ManyToManyField(
        Attribute,
        related_name="PolicyIncludedAttributes",
        blank=True,
        verbose_name=_("included attributes"),
    )

    excluded_attributes = models.ManyToManyField(
        Attribute,
        related_name="PolicyExcludedAttributes",
        blank=True,
        verbose_name=_("excluded attributes"),
    )

    def __str__(self):
        return self.name

    @staticmethod
    def belongs(computer, attributes):
        for attribute in attributes:
            if attribute.id == 1 or \
                    attribute in computer.sync_attributes.all():
                return True

        return False

    @staticmethod
    def belongs_excluding(computer, included_attributes, excluded_attributes):
        if Policy.belongs(computer, included_attributes) and \
                not Policy.belongs(computer, excluded_attributes):
            return True

        return False

    @staticmethod
    def get_packages_to_remove(group, project_id=0):
        _packages = []
        for item in PolicyGroup.objects.filter(policy=group.policy).exclude(id=group.id):
            for pkgs in item.applications.filter(
                packages_by_project__project__id=project_id
            ).values_list(
                'packages_by_project__packages_to_install',
                flat=True
            ):
                _packages.extend(to_list(pkgs))

        return _packages

    @staticmethod
    def get_packages(computer):
        to_install = []
        to_remove = []

        for policy in Policy.objects.filter(enabled=True):
            if policy.belongs_excluding(
                    computer,
                    policy.included_attributes.all(),
                    policy.excluded_attributes.all()
            ):
                for group in PolicyGroup.objects.filter(
                        policy=policy
                ).order_by("priority"):
                    if policy.belongs_excluding(
                            computer,
                            group.included_attributes.all(),
                            group.excluded_attributes.all()
                    ):
                        for pkgs in group.applications.filter(
                                packages_by_project__project__id=computer.project.id
                        ).values_list(
                            'packages_by_project__packages_to_install',
                            flat=True
                        ):
                            to_install.extend(to_list(pkgs))

                        if policy.exclusive:
                            to_remove.extend(
                                policy.get_packages_to_remove(group, computer.project.id)
                            )
                        break

        return to_install, to_remove

    class Meta:
        app_label = 'catalog'
        verbose_name = _("Policy")
        verbose_name_plural = _("Policies")
        unique_together = ("name",)
        permissions = (("can_save_policy", "Can save Policy"),)
        ordering = ['name']


class PolicyGroup(models.Model, MigasLink):
    priority = models.IntegerField(
        verbose_name=_("priority")
    )

    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        verbose_name=_("policy")
    )

    included_attributes = models.ManyToManyField(
        Attribute,
        related_name="PolicyGroupIncludedAttributes",
        blank=True,
        verbose_name=_("included attributes"),
    )

    excluded_attributes = models.ManyToManyField(
        Attribute,
        related_name="PolicyGroupExcludedAttributes",
        blank=True,
        verbose_name=_("excluded attributes"),
    )

    applications = models.ManyToManyField(
        Application,
        blank=True,
        verbose_name=_("application"),
    )

    def __str__(self):
        return '{} ({})'.format(self.policy.name, self.priority)

    class Meta:
        app_label = 'catalog'
        verbose_name = _("Policy Group")
        verbose_name_plural = _("Policy Groups")
        unique_together = (("policy", "priority"),)
        permissions = (("can_save_policygroup", "Can save Policy Group"),)
        ordering = ['policy__name', 'priority']


@receiver(pre_save, sender=Application)
def pre_save_application(sender, instance, **kwargs):
    if not instance.pk and not hasattr(instance, _UNSAVED_IMAGEFIELD):
        setattr(instance, _UNSAVED_IMAGEFIELD, instance.icon)
        instance.icon = None


@receiver(post_save, sender=Application)
def post_save_application(sender, instance, created, **kwargs):
    if created and hasattr(instance, _UNSAVED_IMAGEFIELD):
        instance.icon = getattr(instance, _UNSAVED_IMAGEFIELD)
        instance.save()
        instance.__dict__.pop(_UNSAVED_IMAGEFIELD)
