# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models.common import link
from migasfree.server.models import DeviceType, DeviceManufacturer, \
    DeviceConnection, DeviceFile


class DeviceModel(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        null=True,
        blank=True
    )

    manufacturer = models.ForeignKey(
        DeviceManufacturer,
        verbose_name=unicode(_("manufacturer"))
    )

    devicetype = models.ForeignKey(
        DeviceType,
        verbose_name=unicode(_("type"))
    )

    devicefile = models.ForeignKey(
        DeviceFile,
        null=True,
        blank=True,
        verbose_name=unicode(_("file"))
    )

    connections = models.ManyToManyField(
        DeviceConnection,
        null=True,
        blank=True,
        verbose_name=unicode(_("connections"))
    )

    preinstall = models.TextField(
        unicode(_("pre-install")),
        null=True,
        blank=True,
        help_text="pre-install"
    )

    postinstall = models.TextField(
        unicode(_("post-install")),
        null=True,
        blank=True,
        help_text="post-install"
    )

    preremove = models.TextField(
        unicode(_("pre-remove")),
        null=True,
        blank=True,
        help_text="pre-remove"
    )

    postremove = models.TextField(
        unicode(_("post-remove")),
        null=True,
        blank=True,
        help_text="post-remove"
    )

    def __unicode__(self):
        return u'%s-%s' % (str(self.manufacturer), str(self.name))

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "_")
        self.preinstall = self.preinstall.replace("\r\n", "\n")
        self.postinstall = self.postinstall.replace("\r\n", "\n")
        self.preremove = self.preremove.replace("\r\n", "\n")
        self.postremove = self.postremove.replace("\r\n", "\n")
        super(DeviceModel, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Device (Model)"))
        verbose_name_plural = unicode(_("Device (Models)"))
        unique_together = (("devicetype", "manufacturer", "name"),)
        permissions = (("can_save_devicemodel", "Can save Device Model"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
