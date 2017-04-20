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

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name=_('project')
    )

    name = models.CharField(verbose_name=_('name'), max_length=50)

    description = MarkdownxField(
        verbose_name=_('description'),
        blank=True,
        help_text=_('markdown syntax allowed')
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('date'))

    packages_to_install = models.TextField(
        verbose_name=_('packages to install'),
        blank=True,
    )

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
        unique_together = (("name", "project"),)
        permissions = (('can_save_application', 'Can save application'),)
