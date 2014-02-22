# -*- coding: utf-8 *-*

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models import Device, DeviceFeature, DeviceDriver


class DeviceLogical(models.Model):
    device = models.ForeignKey(
        Device,
        verbose_name=_("device")
    )

    feature = models.ForeignKey(
        DeviceFeature,
        verbose_name=_("feature")
    )

    def datadict(self, oVersion):
        dictdevice = self.device.datadict()
        try:
            oDeviceDriver = DeviceDriver.objects.filter(
                version__id=oVersion.id,
                model__id=self.device.model.id,
                feature__id=self.feature.id
            )[0]
            if oDeviceDriver:
                dictdriver = oDeviceDriver.datadict()
        except:
            dictdriver = {}

        return {
            "devicelogical_id": self.id,
            "device": dictdevice,
            "driver": dictdriver
        }

    def computers_link(self):
        ret = ""
        for c in self.computer_set.all():
            ret += c.link() + " "
        return ret

    computers_link.allow_tags = True
    computers_link.short_description = _("Computers")

    def save(self, *args, **kwargs):
        super(DeviceLogical, self).save(*args, **kwargs)
        self.reinstall()

    def reinstall(self):
        for computer in self.computer_set.all():
            computer.remove_device_copy(self.id)

    def __unicode__(self):
        return "%s-%s-%s" % (
            self.device.name,
            self.device.model.name,
            self.feature.name
        )

    class Meta:
        app_label = 'server'
        verbose_name = _("Device (Logical)")
        verbose_name_plural = _("Device (Logical)")
        permissions = (("can_save_devicelogical", "Can save Device Logical"),)
        unique_together = (("device", "feature"),)
