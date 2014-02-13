# -*- coding: utf-8 -*-

import os

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from migasfree.settings import MIGASFREE_REPO_DIR

from migasfree.server.models import Version, VersionManager, \
    Store, user_version


class Package(models.Model):
    name = models.CharField(
        _("name"),
        max_length=100
    )

    version = models.ForeignKey(
        Version,
        verbose_name=_("version")
    )

    store = models.ForeignKey(
        Store,
        verbose_name=_("store")
    )

    objects = VersionManager()  # manager by user version

    def create_dir(self):
        _path = os.path.join(
            MIGASFREE_REPO_DIR,
            self.version.name,
            'STORES',
            self.store.name,
            self.name
        )
        if not os.path.exists(_path):
            os.makedirs(_path)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Package/Set")
        verbose_name_plural = _("Packages/Sets")
        unique_together = (("name", "version"),)
        permissions = (("can_save_package", "Can save Package"),)

    def link(self):
        info = "%sSTORES/%s/%s/?version=%s" % (
            reverse('package_info', args=('', )),
            self.store.name,
            self.name,
            self.version.name
        )

        pkg_info = self.__unicode__()
        if self.version == user_version():
            pkg_info = '<a href="%s">%s</a>' % (
                reverse('admin:server_package_change', args=(self.id, )),
                self.__unicode__()
            )

        return format_html(
            '<a href="%s" class="fa fa-archive" title="%s"></a> %s' % (
                info,
                _("information"),
                pkg_info
            )
        )

    link.short_description = Meta.verbose_name
    link.allow_tags = True
