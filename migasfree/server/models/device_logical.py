# -*- coding: utf-8 *-*

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models import (
    Device,
    DeviceFeature,
    DeviceDriver,
    MigasLink
)


class DeviceLogical(models.Model, MigasLink):
    device = models.ForeignKey(
        Device,
        verbose_name=_("device")
    )

    feature = models.ForeignKey(
        DeviceFeature,
        verbose_name=_("feature")
    )

    def datadict(self, version):
        dictdevice = self.device.datadict()
        try:
            device_driver = DeviceDriver.objects.filter(
                version__id=version.id,
                model__id=self.device.model.id,
                feature__id=self.feature.id
            )[0]
            if device_driver:
                dictdriver = device_driver.datadict()
        except:
            dictdriver = {}

        ret = {
            self.device.connection.devicetype.name: {
                'feature': self.feature.name,
                'id': self.id,
            }
        }
        for key, value in dictdevice.items():
            ret[self.device.connection.devicetype.name][key] = value
        for key, value in dictdriver.items():
            ret[self.device.connection.devicetype.name][key] = value

        return ret

    def computers_link(self):
        ret = ""
        for computer in self.computer_set.all():
            ret += computer.link() + " "
        return ret

    computers_link.allow_tags = True
    computers_link.short_description = _("Computers")

    def save(self, *args, **kwargs):
        super(DeviceLogical, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s__%s__%s__%s' % (
            self.device.name,
            self.device.model.name,
            self.feature.name,
            str(self.id)
        )

    class Meta:
        app_label = 'server'
        verbose_name = _("Device (Logical)")
        verbose_name_plural = _("Device (Logical)")
        permissions = (("can_save_devicelogical", "Can save Device Logical"),)
        unique_together = (("device", "feature"),)
