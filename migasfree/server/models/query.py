# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Query(models.Model):
    name = models.CharField(
        _("name"),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    description = models.TextField(
        _("description"),
        null=True,
        blank=True
    )

    code = models.TextField(
        _("code"),
        null=True,
        blank=True,
        help_text=_("Code Django: version=user.version, query=QuerySet, fields=list of QuerySet fields names to show, titles=list of QuerySet fields titles"),
        default="query=Package.objects.filter(version=VERSION).filter(Q(repository__id__exact=None))\nfields=('id','name','store__name')\ntitles=('id','name','store')"
    )

    parameters = models.TextField(
        _("parameters"),
        null=True,
        blank=True,
        help_text="Code Django: "
    )

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Query")
        verbose_name_plural = _("Queries")
        permissions = (("can_save_query", "Can save Query"),)


def get_query_names():
    result = []
    for item in Query.objects.all().order_by("-id"):
        result.append([item.id, item.name])

    return result
