# -*- coding: utf-8 *-*

from past.builtins import basestring

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from . import (
    Device,
    DeviceFeature,
    DeviceDriver,
    Attribute,
    MigasLink
)


class DeviceLogicalManager(models.Manager):
    def create(self, device, feature, alternative_feature_name=None):
        obj = DeviceLogical(
            device=device,
            feature=feature,
            alternative_feature_name=alternative_feature_name
        )
        obj.save()

        return obj

    def scope(self, user):
        qs = super(DeviceLogicalManager, self).get_queryset()
        if not user.is_view_all():
            atts=user.get_attributes()
            qs = qs.filter(attributes__in=atts).distinct()

        return qs


@python_2_unicode_compatible
class DeviceLogical(models.Model, MigasLink):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        verbose_name=_("device")
    )

    feature = models.ForeignKey(
        DeviceFeature,
        on_delete=models.CASCADE,
        verbose_name=_("feature")
    )

    alternative_feature_name = models.CharField(
        verbose_name=_('alternative feature name'),
        max_length=50,
        null=True,
        blank=True,
        unique=False
    )

    attributes = models.ManyToManyField(
        Attribute,
        blank=True,
        verbose_name=_("attributes"),
        help_text=_("Assigned Attributes")
    )

    objects = DeviceLogicalManager()

    _include_links = ["device - devicelogical", ]

    def get_name(self):
        return self.alternative_feature_name if self.alternative_feature_name else self.feature.name

    def as_dict(self, project):
        driver_as_dict = {}
        try:
            driver = DeviceDriver.objects.filter(
                project__id=project.id,
                model__id=self.device.model.id,
                feature__id=self.feature.id
            )[0]
            if driver:
                driver_as_dict = driver.as_dict()
        except IndexError:
            pass

        ret = {
            self.device.connection.device_type.name: {
                'feature': self.get_name(),
                'id': self.id,
                'manufacturer': self.device.model.manufacturer.name
            }
        }

        device_as_dict = self.device.as_dict()
        for key, value in list(device_as_dict.items()):
            ret[self.device.connection.device_type.name][key] = value

        for key, value in list(driver_as_dict.items()):
            ret[self.device.connection.device_type.name][key] = value

        return ret

    def __str__(self):
        return u'{}__{}__{}__{}__{}'.format(
            self.device.model.manufacturer.name,
            self.device.model.name,
            self.feature.name,
            self.device.name,
            self.id
        )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if isinstance(self.alternative_feature_name, basestring):
            self.alternative_feature_name = self.alternative_feature_name.replace(" ", "_")

        super(DeviceLogical, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        app_label = 'server'
        verbose_name = _("Device Logical")
        verbose_name_plural = _("Devices Logical")
        permissions = (("can_save_devicelogical", "Can save Device Logical"),)
        unique_together = (("device", "feature"),)
