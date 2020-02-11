# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..utils import to_list
from . import Project, DeviceModel, DeviceFeature


class DeviceDriver(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        null=True,
        blank=True,
    )

    model = models.ForeignKey(
        DeviceModel,
        on_delete=models.CASCADE,
        verbose_name=_("model")
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name=_("project")
    )

    feature = models.ForeignKey(
        DeviceFeature,
        on_delete=models.CASCADE,
        verbose_name=_("feature")
    )

    packages_to_install = models.TextField(
        verbose_name=_("packages to install"),
        null=True,
        blank=True
    )

    def as_dict(self):
        return {
            'driver': self.name if self.name else '',
            'packages': to_list(self.packages_to_install),
        }

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.packages_to_install = self.packages_to_install.replace(
            "\r\n", "\n"
        )
        super(DeviceDriver, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name.split("/")[-1] if self.name else ''

    class Meta:
        app_label = 'server'
        verbose_name = _("Driver")
        verbose_name_plural = _("Drivers")
        permissions = (("can_save_devicedriver", "Can save Device Driver"),)
        unique_together = (("model", "project", "feature"),)
        ordering = ['model', 'name']
