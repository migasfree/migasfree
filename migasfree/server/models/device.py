# -*- coding: utf-8 -*-

import json

from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

from . import DeviceConnection, DeviceModel, Attribute, MigasLink

from ..utils import (
    swap_m2m,
    remove_empty_elements_from_dict
)


class DeviceManager(models.Manager):
    def scope(self, user):
        qs = super(DeviceManager, self).get_queryset()
        if not user.is_view_all():
            qs = qs.filter(
                devicelogical__attributes__in=user.get_attributes()
            ).distinct()

        return qs


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

    objects = DeviceManager()

    def menu_link(self, request):
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
                    [ugettext('HTTP'), address, _('web access to the device')]
                ]

        return super(Device, self).menu_link(request)

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

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        data = json.loads(self.data)
        if 'NAME' in data:
            data['NAME'] = data['NAME'].replace(' ', '_')
            self.data = json.dumps(data)

        super(Device, self).save(force_insert, force_update, using, update_fields)

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
        return self.devicelogical_set.exclude(attributes=None)

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
            ugettext("Device"): '{} - {}'.format(self.link(), self.location()),
            ugettext("Logical devices"): '<br />' +
            '<br />'.join(
                str(x.feature) + ': ' + ', '.join(
                    c.link() for c in x.attributes.all()
                )
                for x in self.devicelogical_set.order_by('feature')
            ),
        })

    def related_objects(self, model, user):
        """
        Return Queryset with the related computers based in devicelogical_attributes
        """
        from migasfree.server.models import Computer, Attribute
        if model == 'computer':

            return Computer.productive.scope(user).filter(
                sync_attributes__in=Attribute.objects.filter(devicelogical__device__id=self.id)
            ).distinct()

        return None

    class Meta:
        app_label = 'server'
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        unique_together = (("connection", "name"),)
        permissions = (("can_save_device", "Can save Device"),)
