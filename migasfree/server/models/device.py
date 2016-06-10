# -*- coding: utf-8 -*-

import json

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _

from . import DeviceConnection, DeviceModel, MigasLink


@python_2_unicode_compatible
class Device(models.Model, MigasLink):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    model = models.ForeignKey(
        DeviceModel,
        verbose_name=_("model")
    )

    connection = models.ForeignKey(
        DeviceConnection,
        verbose_name=_("connection")
    )

    data = models.TextField(
        verbose_name=_("data"),
        null=True,
        blank=False,
        default="{}"
    )

    def __init__(self, *args, **kwargs):
        super(Device, self).__init__(*args, **kwargs)

        if self.id:
            data = json.loads(self.data)
            ip = data.get('IP', None)
            if ip:
                address = 'http://%s' % ip
            else:
                try:
                    address = 'http://%s:631' % \
                        self.devicelogical_set.all()[0].computer_set.all()[0].ip
                except:
                    address = ''

            if address:
                self._actions = [
                    [ugettext('Go to %s' % self.model), address]
                ]

    def location(self):
        data = json.loads(self.data)
        return data.get('LOCATION', '')

    def model_link(self):
        return self.model.link()

    model_link.short_description = _("Device Model")
    model_link.allow_tags = True

    def datadict(self):
        return {
            'name': self.name,
            'model': self.model.name,
            self.connection.name: json.loads(self.data),
        }

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        data = json.loads(self.data)
        if 'NAME' in data:
            data['NAME'] = data['NAME'].replace(' ', '_')
            self.data = json.dumps(data)

        super(Device, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        unique_together = (("connection", "name"),)
        permissions = (("can_save_device", "Can save Device"),)


@receiver(pre_save, sender=Device)
def pre_save_device(sender, instance, **kwargs):
    if instance.id:
        old_obj = Device.objects.get(pk=instance.id)
        if old_obj.data != instance.data or \
                old_obj.name != instance.name or \
                old_obj.connection.id != instance.connection.id or \
                old_obj.model.id != instance.model.id:
            for logical_device in instance.devicelogical_set.all():
                for computer in logical_device.computer_set.all():
                    computer.remove_device_copy(logical_device.id)
