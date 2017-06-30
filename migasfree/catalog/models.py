# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from markdownx.models import MarkdownxField

from migasfree.server.models import Project, MigasLink


@python_2_unicode_compatible
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
        upload_to='catalog_icons/',
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

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'catalog'
        verbose_name = _('Application')
        verbose_name_plural = _('Applications')
        permissions = (('can_save_application', 'Can save application'),)


@python_2_unicode_compatible
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

    def repr_packages_to_install(self):
        return self.packages_to_install.replace('\n', ' ').split()

    def __str__(self):
        return u'{}@{}'.format(self.application, self.project)

    class Meta:
        app_label = 'catalog'
        verbose_name = _('Packages by Project')
        verbose_name_plural = _('Packages by Projects')
        unique_together = (('application', 'project'),)
        permissions = (('can_save_packagesbyproject', 'Can save packages by project'),)
