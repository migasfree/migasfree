# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import Project, DeviceModel, DeviceFeature


@python_2_unicode_compatible
class DeviceDriver(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        null=True,
        blank=True,
    )

    model = models.ForeignKey(
        DeviceModel,
        verbose_name=_("model")
    )

    project = models.ForeignKey(
        Project,
        verbose_name=_("project")
    )

    feature = models.ForeignKey(
        DeviceFeature,
        verbose_name=_("feature")
    )

    install = models.TextField(
        verbose_name=_("packages to install"),
        null=True,
        blank=True
    )

    def as_dict(self):
        lst_install = []
        for p in self.install.replace("\r", " ").replace("\n", " ").split(" "):
            if p != '' and p != 'None':
                lst_install.append(p)

        return {
            'driver': self.name,
            'packages': lst_install,
        }

    def save(self, *args, **kwargs):
        self.install = self.install.replace("\r\n", "\n")
        super(DeviceDriver, self).save(*args, **kwargs)

    def __str__(self):
        return self.name.split("/")[-1]

    class Meta:
        app_label = 'server'
        verbose_name = _("Driver")
        verbose_name_plural = _("Drivers")
        permissions = (("can_save_devicedriver", "Can save Device Driver"),)
        unique_together = (("model", "project", "feature"),)
        ordering = ['model', 'name']
