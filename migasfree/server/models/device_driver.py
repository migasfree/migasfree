# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from common import link
from migasfree.server.models import Version, DeviceModel, DeviceFeature


class DeviceDriver(models.Model):

    name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    model = models.ForeignKey(
        DeviceModel,
        verbose_name=_("model")
    )

    version = models.ForeignKey(
        Version,
        verbose_name=_("version")
    )

    feature = models.ForeignKey(
        DeviceFeature,
        verbose_name=_("feature")
    )

    install = models.TextField(
        _("packages to install"),
        null=True,
        blank=True
    )

    def datadict(self):
        lst_install = []
        for p in self.install.replace("\r", " ").replace("\n", " ").split(" "):
            if p != "" and p != 'None':
                lst_install.append(p)

        return {'driver_id': self.id,
            'driver': self.name,
            'feature': self.feature.name,
            'packages': lst_install,
             }

    def save(self, *args, **kwargs):
        self.install = self.install.replace("\r\n", "\n")
        super(DeviceDriver, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % (str(self.name).split("/")[-1])

    class Meta:
        app_label = 'server'
        verbose_name = _("Device (Driver)")
        verbose_name_plural = _("Device (Driver)")
        permissions = (("can_save_devicedriver", "Can save Device Driver"),)
        unique_together = (("model", "version", "feature"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
