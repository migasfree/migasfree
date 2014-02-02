# -*- coding: utf-8 -*-

import os
import datetime
import shutil

from django.db import models
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from migasfree.server.functions import horizon
from migasfree.settings import MIGASFREE_REPO_DIR

from migasfree.server.models.common import link
from migasfree.server.models import Version, Package, Attribute, Schedule, \
    VersionManager, ScheduleDelay


class Repository(models.Model):
    name = models.CharField(
        _("name"),
        max_length=50
    )

    version = models.ForeignKey(
        Version,
        verbose_name=_("version")
    )

    packages = models.ManyToManyField(
        Package,
        null=True,
        blank=True,
        verbose_name=_("Packages/Set"),
        help_text=_("Assigned Packages")
    )

    attributes = models.ManyToManyField(
        Attribute,
        null=True,
        blank=True,
        verbose_name=_("attributes"),
        help_text=_("Assigned Attributes")
    )

    excludes = models.ManyToManyField(
        Attribute,
        related_name="ExcludeAttribute",
        null=True,
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
        _("active"),
        default=True,
        help_text=_("if you uncheck this field, the repository is hidden for all computers.")
    )

    date = models.DateField(
        _("date"),
        help_text=_("Date initial for distribute.")
    )

    comment = models.TextField(
        _("comment"),
        null=True,
        blank=True
    )

    toinstall = models.TextField(
        _("packages to install"),
        null=True,
        blank=True
    )

    toremove = models.TextField(
        _("packages to remove"),
        null=True,
        blank=True
    )

    defaultpreinclude = models.TextField(
        _("default preinclude packages"),
        null=True,
        blank=True
    )

    defaultinclude = models.TextField(
        _("default include packages"),
        null=True,
        blank=True
    )

    defaultexclude = models.TextField(
        _("default exclude packages"),
        null=True,
        blank=True
    )

    objects = VersionManager()  # manager by user version

    def packages_link(self):
        ret = ""
        for pack in self.packages.all():
            ret += pack.link() + " "

        return ret

    packages_link.allow_tags = True
    packages_link.short_description = _("Packages")

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "_")
        self.toinstall = self.toinstall.replace("\r\n", "\n")
        self.toremove = self.toremove.replace("\r\n", "\n")
        super(Repository, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # remove the directory of repository
        path = os.path.join(
            MIGASFREE_REPO_DIR,
            self.version.name,
            self.version.pms.slug,
            self.name
        )
        if os.path.exists(path):
            shutil.rmtree(path)
        super(Repository, self).delete(*args, **kwargs)

    def timeline(self):
        if self.schedule is None or self.schedule.id is None:
            return _('Without schedule')

        delays = ScheduleDelay.objects.filter(
            schedule__id=self.schedule.id
        ).order_by('delay')

        date_format = "%Y-%m-%d"
        end_date = datetime.datetime.strptime(
            str(horizon(self.date, delays.reverse()[0].delay)),
            date_format
        )
        begin_date = datetime.datetime.strptime(
            str(horizon(self.date, delays[0].delay)),
            date_format
        )

        delta = end_date - begin_date
        progress = datetime.datetime.now() - begin_date
        number = float(progress.days) / delta.days * 100
        if number > 100:
            number = 100

        ret = '<div class="progress" title="%(number)d%%"><div class="progress-bar progress-bar-success" role="progressbar" aria-valuenow="%(number)d" aria-valuemin="0" aria-valuemax="100" style="width: %(number)d%%"><span class="sr-only">%(number)d%% complete</span></div></div>' % {
            'number': number
        }

        ret += str(self.schedule) + ' <div class="btn-group btn-group-xs timeline">'
        ret += '<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown"><span class="caret"></span><span class="sr-only">Toggle Dropdown</span></button>'
        ret += '<ul class="dropdown-menu">'

        now = datetime.datetime.now().date()
        for item in delays:
            ret += '<li class="list-group-item">'
            ret += '<p class="list-group-item-heading label label-'
            hori = horizon(self.date, item.delay)
            if hori <= now:
                ret += 'success'
            else:
                ret += 'default'
            ret += '">' + hori.strftime("%a-%b-%d") + '</p>'
            ret += '<p class="list-group-item-text">'
            for e in item.attributes.values_list("value"):
                ret += e[0] + " "

            ret += '</p></li>'

        return format_html(ret + '</ul></div>')

    timeline.allow_tags = True
    timeline.short_description = _('timeline')

    class Meta:
        app_label = 'server'
        verbose_name = _("Repository")
        verbose_name_plural = _("Repositories")
        unique_together = (("name", "version"),)
        permissions = (("can_save_repository", "Can save Repository"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
