# -*- coding: utf-8 -*-

import json

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _

from . import DeviceConnection, DeviceModel, Attribute, MigasLink

from ..utils import (
    swap_m2m,
    remove_empty_elements_from_dict
)


@python_2_unicode_compatible
class Device(models.Model, MigasLink):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=50,
        unique=True
    )

    model = models.ForeignKey(
        DeviceModel,
        on_delete=models.CASCADE,
        verbose_name=_("model")
    )

    connection = models.ForeignKey(
        DeviceConnection,
        on_delete=models.CASCADE,
        verbose_name=_("connection")
    )

    available_for_attributes = models.ManyToManyField(
        Attribute,
        blank=True,
        verbose_name=_("available for attributes")
    )

    data = models.TextField(
        verbose_name=_("data"),
        null=True,
        default="{}"
    )

    def menu_link(self, user):
        if self.id:
            data = json.loads(self.data)
            ip = data.get('IP', None)
            if ip:
                address = 'http://{}'.format(ip)
            else:
                try:
                    address = 'http://{}:631'.format(
                        self.devicelogical_set.all()[0].attributes.all()[0].ip
                    )
                except:
                    address = ''

            if address:
                self._actions = [
                    [ugettext('Go to %s' % self.model), address]
                ]

        return super(Device, self).menu_link(user)

    def location(self):
        data = json.loads(self.data)
        return data.get('LOCATION', '')

    def as_dict(self):
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

    def incompatible_features(self, target):
        features = []
        for x in self.logical_devices_allocated():
            if target.devicelogical_set.filter(feature=x.feature).count() == 0:
                features.append(str(x.feature))

        for x in target.logical_devices_allocated():
            if self.devicelogical_set.filter(feature=x.feature).count() == 0:
                features.append(str(x.feature))

        return features

    def common_features_allocated(self, target):
        features = []
        for x in self.logical_devices_allocated():
            if target.devicelogical_set.filter(feature=x.feature).count() > 0:
                features.append(x.feature)

        for x in target.logical_devices_allocated():
            if self.devicelogical_set.filter(feature=x.feature).count() > 0:
                if x.feature not in features:
                    features.append(x.feature)

        return features

    def logical_devices_allocated(self):
        return self.devicelogical_set.all().exclude(attributes=None)

    @staticmethod
    def replacement(source, target):
        # Moves computers from logical device
        for feature in source.common_features_allocated(target):
            swap_m2m(
                source.devicelogical_set.get(feature=feature).attributes,
                target.devicelogical_set.get(feature=feature).attributes
            )

    def get_replacement_info(self):
        return remove_empty_elements_from_dict({
            ugettext("Device"): u'{} - {}'.format(self.link(), self.location()),
            ugettext("Logical devices"): '<br />' +
            '<br />'.join(
                str(x.feature) + ': ' + ', '.join(
                    c.link() for c in x.attributes.all()
                )
                for x in self.devicelogical_set.all().order_by('feature')
            ),
        })

    class Meta:
        app_label = 'server'
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        unique_together = (("connection", "name"),)
        permissions = (("can_save_device", "Can save Device"),)
