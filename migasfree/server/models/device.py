# -*- coding: utf-8 -*-

import os

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.settings import MIGASFREE_TMP_DIR

from migasfree.server.models.common import link
from migasfree.server.models import DeviceConnection, DeviceModel


class Device(models.Model):

    def device_connection_name(self):
        return u"%s" % (self.connection.name)

    device_connection_name.short_description = unicode(_('Port'))

    def device_connection_type(self):
        return u"%s" % (self.connection.devicetype.name)

    device_connection_type.short_description = unicode(_('Type'))

    def device_manufacturer_name(self):
        return u"%s" % (self.model.manufacturer.name)

    device_manufacturer_name.short_description = unicode(_('Manufacturer'))

    name = models.CharField(
        unicode(_("Identification number")),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    alias = models.CharField(
        unicode(_("Alias")),
        max_length=50,
        null=True,
        blank=True
    )

    model = models.ForeignKey(
        DeviceModel,
        verbose_name=unicode(_("model"))
    )

    connection = models.ForeignKey(
        DeviceConnection,
        verbose_name=unicode(_("connection"))
    )

    uri = models.CharField(
        unicode(_("uri")),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    location = models.CharField(
        unicode(_("location")),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    information = models.CharField(
        unicode(_("information")),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    def computers_link(self):
        ret = ""
        for c in self.computer_set.all():
            ret += c.link() + " "
        return ret

    computers_link.allow_tags = True
    computers_link.short_description = unicode(_("Computers"))

    def fullname(self):
        if self.alias == "":
            return u'%s-%s_[%s]' % (
                self.model.manufacturer.name,
                self.model.name,
                self.name
            )
        else:
            return u'%s_[%s]' % (self.alias, self.name)

    def data(self):
        return {
            "NUMBER": self.name,
            "NAME": self.fullname(),
            "ALIAS": self.alias,
            "TYPE": self.model.devicetype.name,
            "MANUFACTURER": self.model.manufacturer.name,
            "MODEL": self.model.name,
            "URI": self.uri,
            "PORT": self.connection.name,
            "LOCATION": self.location,
            "INFORMATION": self.information
        }

    def render_install(self):  # DEPRECATED
        ret = self.values + "\n"

        #Spaces in device name is not allowed.
        ret += "_NAME=`echo $_NAME|sed \"s/ /_/g\"`\n"

        #codes
        ret += self.model.preinstall + "\n"
        ret += self.connection.install + "\n"
        ret += self.model.postinstall + "\n"

        #replaces
        ret = ret.replace(
            "$_FILE",
            os.path.join(MIGASFREE_TMP_DIR, str(self.model.devicefile.name))
        )
        ret = ret.replace("$_NUMBER", self.name)
        ret = ret.replace("$_DEVICETYPE", self.connection.devicetype.name)
        ret = ret.replace("$_MANUFACTURER", self.model.manufacturer.name)
        ret = ret.replace("$_MODEL", self.model.name)
        ret = ret.replace("$_PORT", self.connection.name)

        return ret

    def render_remove(self):  # DEPRECATED
        ret = self.values + "\n"

        #Spaces in device name is not allowed.
        ret += "_NAME=`echo $_NAME|sed \"s/ /_/g\"`\n"

        #codes
        ret += self.model.preremove + "\n"
        ret += self.connection.remove + "\n"
        ret += self.model.postremove + "\n"

        #replaces
        ret = ret.replace(
            "$_FILE",
            os.path.join(MIGASFREE_TMP_DIR, str(self.model.devicefile.name))
        )
        ret = ret.replace("$_NUMBER", self.name)
        ret = ret.replace("$_DEVICETYPE", self.connection.devicetype.name)
        ret = ret.replace("$_MANUFACTURER", self.model.manufacturer.name)
        ret = ret.replace("$_MODEL", self.model.name)
        ret = ret.replace("$_PORT", self.connection.name)
        return ret

    def save(self, *args, **kwargs):
#        if self.values is None or self.values == "":
#            self.values=""
#            for p in self.connection.fields.split(" "):
#                self.values += "_" + p + "=''\n"
#        self.values = self.values.replace("\r\n","\n")

        if self.uri is None or self.uri == "":
            self.uri = self.connection.uri

        super(Device, self).save(*args, **kwargs)
        for computer in self.computer_set.all():
            #remove the device in devices_copy
            computer.devices_modified = True
            computer.save()

    def __unicode__(self):
        return u'%s-%s-%s' % (self.name, self.model.name, self.connection.name)

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Device"))
        verbose_name_plural = unicode(_("Devices"))
        unique_together = (("connection", "name"),)
        permissions = (("can_save_device", "Can save Device"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
