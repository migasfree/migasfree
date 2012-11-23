# -*- coding: utf-8 -*-

import os
import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.functions import horizon
from migasfree.settings import MIGASFREE_REPO_DIR

from migasfree.server.models.common import link
from migasfree.server.models import Version, Package, Attribute, Schedule, \
    VersionManager, ScheduleDelay


class Repository(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=50
    )

    version = models.ForeignKey(
        Version,
        verbose_name=unicode(_("version"))
    )

    packages = models.ManyToManyField(
        Package,
        null=True,
        blank=True,
        verbose_name=unicode(_("Packages/Set")),
        help_text="Assigned Packages"
    )

    attributes = models.ManyToManyField(
        Attribute,
        null=True,
        blank=True,
        verbose_name=unicode(_("attributes")),
        help_text="Assigned Attributes"
    )

    excludes = models.ManyToManyField(
        Attribute,
        related_name="ExcludeAttribute",
        null=True,
        blank=True,
        verbose_name=unicode(_("excludes")),
        help_text="Excluded Attributes"
    )

    schedule = models.ForeignKey(
        Schedule,
        null=True,
        blank=True,
        verbose_name=unicode(_("schedule"))
    )

    createpackages = models.ManyToManyField(
        Package,
        null=True,
        blank=True,
        verbose_name=unicode(_("createpackages")),
        related_name="createpackages",
        editable=False
    )  # used to know when "createrepositories"

    active = models.BooleanField(
        unicode(_("active")),
        default=True,
        help_text=unicode(_("if you uncheck this field, the repository is hidden for all computers."))
    )

    date = models.DateField(
        unicode(_("date")),
        help_text=unicode(_("Date initial for distribute."))
    )

    comment = models.TextField(
        unicode(_("comment")),
        null=True,
        blank=True
    )

    toinstall = models.TextField(
        unicode(_("packages to install")),
        null=True,
        blank=True
    )

    toremove = models.TextField(
        unicode(_("packages to remove")),
        null=True,
        blank=True
    )

    modified = models.BooleanField(
        unicode(_("modified")),
        default=False,
        editable=False
    )  # used to "createrepositories"

    objects = VersionManager()  # manager by user version

    def packages_link(self):
        ret = ""
        for pack in self.packages.all():
            ret += pack.link() + " "

        return ret

    packages_link.allow_tags = True
    packages_link.short_description = unicode(_("Packages"))

    def __unicode__(self):
        return u'%s' % (self.name)

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "_")
        self.toinstall = self.toinstall.replace("\r\n", "\n")
        self.toremove = self.toremove.replace("\r\n", "\n")
        super(Repository, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # remove the directory of repository
        _path = os.path.join(
            MIGASFREE_REPO_DIR,
            self.version.name,
            self.version.pms.slug,
            self.name
        )
        os.system("rm -rf %s" % _path)
        super(Repository, self).delete(*args, **kwargs)

    def timeline(self):
        ret = '<table class="">'
        delays = ScheduleDelay.objects.filter(
            schedule__id=self.schedule.id
        ).order_by('delay')

        for d in delays:
            hori = horizon(self.date, d.delay)
            if hori <= datetime.now().date():
                ret += '<tr class=""><td><b>'
                l = d.attributes.values_list("value")
                ret += "<b>" + hori.strftime("%a-%b-%d") + "</b></td><td><b>"
                for e in l:
                    ret += e[0] + " "
                ret += "</b></td></tr>"
            else:
                ret += '<tr class=""><td>'
                l = d.attributes.values_list("value")
                ret += hori.strftime("%a-%b-%d") + "</td><td>"
                for e in l:
                    ret += e[0] + " "

                ret += "</td></tr>"

        return ret + "</table>"

    timeline.allow_tags = True
    timeline.short_description = unicode(_('timeline'))

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Repository"))
        verbose_name_plural = unicode(_("Repositories"))
        unique_together = (("name", "version"),)
        permissions = (("can_save_repository", "Can save Repository"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
