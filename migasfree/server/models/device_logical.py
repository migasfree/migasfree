# -*- coding: utf-8 *-*

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import (
    Device,
    DeviceFeature,
    DeviceDriver,
    MigasLink
)


class DeviceLogicalManager(models.Manager):
    def create(self, device, feature, name=None):
        obj = DeviceLogical(device=device, feature=feature, name=name)
        obj.save()

        return obj


@python_2_unicode_compatible
class DeviceLogical(models.Model, MigasLink):
    device = models.ForeignKey(
        Device,
        verbose_name=_("device")
    )

    feature = models.ForeignKey(
        DeviceFeature,
        verbose_name=_("feature")
    )

    name = models.CharField(
        verbose_name=_('name'),
        max_length=50,
        null=True,
        blank=True,
        unique=False
    )

    objects = DeviceLogicalManager()

    def get_name(self):
        return self.name if self.name else self.feature.name

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
                'feature': self.get_name(),
                'id': self.id,
                'manufacturer': self.device.model.manufacturer.name
            }
        }
        for key, value in list(dictdevice.items()):
            ret[self.device.connection.devicetype.name][key] = value
        for key, value in list(dictdriver.items()):
            ret[self.device.connection.devicetype.name][key] = value

        return ret

    def device_link(self):
        return self.device.link()

    device_link.short_description = _("Device")
    device_link.allow_tags = True

    def computers_link(self):
        return ' '.join(
            [computer.link() for computer in self.computer_set.all()]
        )

    computers_link.allow_tags = True
    computers_link.short_description = _("Computers")

    def save(self, *args, **kwargs):
        if isinstance(self.name, basestring):
            self.name = self.name.replace(" ", "_")

        super(DeviceLogical, self).save(*args, **kwargs)

    def __str__(self):
        return '%s__%s__%s__%s__%d' % (
            self.device.model.manufacturer.name,
            self.device.model.name,
            self.feature.name,
            self.device.name,
            self.id
        )

    class Meta:
        app_label = 'server'
        verbose_name = _("Device Logical")
        verbose_name_plural = _("Devices Logical")
        permissions = (("can_save_devicelogical", "Can save Device Logical"),)
        unique_together = (("device", "feature"),)
