# -*- coding: utf-8 -*-

import os
from datetime import datetime

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User as UserSystem
from django.contrib.auth.models import UserManager

from migasfree.middleware import threadlocals
from migasfree.server.functions import trans
from migasfree.server.functions import horizon

from migasfree.settings import ADMIN_SITE_ROOT_URL
from migasfree.settings import MIGASFREE_REPO_DIR


from django.utils.translation import ugettext_lazy as _

__all__ = (
    # from common
    'Attribute', 'AutoCheckError', 'MessageServer', 'Checking', 'Pms', 'Property',
    'Query', 'User', 'Version', 'LANGUAGES_CHOICES',

    # from device
    'Device', 'DeviceConnection', 'DeviceFile', 'DeviceManufacturer',
    'DeviceModel', 'DeviceType',

    # from computer
    'Computer', 'Error', 'Login', 'Message', 'Update',

    # from schedule
    'Schedule', 'ScheduleDelay',

    # from repository
    'Package', 'Repository', 'Store', 'UserProfile',

    # from hardware
    'HwCapability', 'HwConfiguration', 'HwLogicalName', 'HwNode',
    'load_hw',

    # from fault
    'Fault', 'FaultDef',
)

# ---- common.py ----

# Programming Language for Properties and FaultDefs
LANGUAGES_CHOICES = (
    (0, 'bash'),
    (1, 'python'),
    (2, 'perl'),
    (3, 'php'),
    (4, 'ruby'),
)

PLATFORM_CHOICES = (
    (0, '---'),
    (1, 'Windows'),
    (2, 'GNU/Linux'),
)


def user_version():
    """
    Return the user version that logged
    """
    try:
        return UserProfile.objects.get(id=threadlocals.get_current_user().id).version
    except:
        return None

def link(obj, description):
    if obj.id == None or obj.id == "":
        return ''
    else:
        return '<a href="%s">%s</a>' % (os.path.join(
            ADMIN_SITE_ROOT_URL,
            'server',
            description.lower(),
            str(obj.id)
        ), obj.__unicode__())

class VersionManager(models.Manager):
    """
    VersionManager is used for filter the property "objects" of somethings class by the version of user logged.
    """
    def get_query_set(self):
        user = user_version()
        if user == None:
            return self.version(0)
        else:
            return self.version(user)

    def version(self, version):
        if version == 0: # return the objects of ALL VERSIONS
            return super(VersionManager, self).get_query_set()
        else: # return only the objects of this VERSION
            return super(VersionManager, self).get_query_set().filter(version=version)

class User(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        unique=True
    )

    fullname = models.CharField(
        unicode(_("fullname")),
        max_length=50
    )

    def __unicode__(self):
        return '%s - %s' % (self.name, self.fullname)

    class Meta:
        verbose_name = unicode(_("User"))
        verbose_name_plural = unicode(_("Users"))
        permissions = (("can_save_user", "Can save User"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class Query(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    description = models.TextField(
        unicode(_("description")),
        null=True,
        blank=True
    )

    code = models.TextField(
        unicode(_("code")),
        null=True,
        blank=True,
        help_text="Code Django: version=user.version, query=QuerySet, fields=list of QuerySet fields names to show, titles=list of QuerySet fields titles",
        default="query=Package.objects.filter(version=VERSION).filter(Q(repository__id__exact=None))\nfields=('id','name','store__name')\ntitles=('id','name','store')"
    )

    parameters = models.TextField(
        unicode(_("parameters")),
        null=True,
        blank=True,
        help_text="Code Django: "
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = unicode(_("Query"))
        verbose_name_plural = unicode(_("Queries"))
        permissions = (("can_save_query", "Can save Query"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class Checking(models.Model):
    """
    For each register of this model, migasfree will show in the section Status of main menu the result of this 'checking'.
    The system only will show the checking if 'result' != 0
    """
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        null=True,
        blank=True,
        help_text=unicode(_("name")),
        unique=True
    )

    description = models.TextField(
        unicode(_("description")),
        null=True,
        blank=True,
        help_text=unicode(_("description"))
    )

    code = models.TextField(
        unicode(_("code")),
        null=False,
        blank=True,
        help_text="Code django. <br><b>VARIABLES TO SETTINGS:</b><br><b>result</b>: a number. If result<>0 the checking is show in the section Status. Default is 0<br><b>icon</b>: name of icon to show localizate in '/repo/icons'. Default is 'information.png'<br><b>url</b>: link. Default is '/migasfree/main'<br><b>msg</b>: The text to show. Default is the field name."
    )

    active = models.BooleanField(
        unicode(_("active")),
        default=True,
        help_text=""
    )

    def save(self, *args, **kwargs):
        self.code = self.code.replace("\r\n", "\n")
        super(Checking, self).save(*args, **kwargs) # Call the "real" save() method

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = unicode(_("Checking"))
        verbose_name_plural = unicode(_("Checkings"))
        permissions = (("can_save_checking", "Can save Checking"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class AutoCheckError(models.Model):
    """
    This model is used to autocheck the errors and marked as 'check' when they are introducing in the system (Sometimes the Package Management System, in the clients, return a string error when in reliaty it is only a warning)
    The origen of this problem is that the package is bad packed.
    """
    message = models.TextField(
        unicode(_("message")),
        null=True,
        blank=True,
        help_text=unicode(_("Text of error that is only a warning. You can copy/paste from the field 'error' of a Error."))
    )

    def save(self, *args, **kwargs):
        self.message = self.message.replace("\r\n", "\n")
        super(AutoCheckError, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.message

    class Meta:
        verbose_name = unicode(_("Auto Check Error"))
        verbose_name_plural = unicode(_("Auto Check Errors"))
        permissions = (("can_save_autocheckerror", "Can save Auto Check Error"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class Pms(models.Model):
    """
    Package Management System

    Each distribution of linux have a P.M.S. For example Fedora uses yum, Ubuntu uses apt, openSUSE zypper, etc.

    By default, migasfree is configured for work whith apt, yum and zypper.

    This model is used for say to migasfree server how must:
        - create the metadata of the repositories in the server.
        - define the source list file of repositories for the client.
        - get info of packages in the server for the view 'Packages Information'.
    """

    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        unique=True
    )

    slug = models.CharField(
        unicode(_("slug")),
        max_length=50,
        null=True,
        blank=True,
        default="REPOSITORIES"
    )

    createrepo = models.TextField(
        unicode(_("create repository")),
        null=True,
        blank=True,
        help_text=unicode(_("Code bash. Define how create the metadata of repositories in the migasfree server."))
    )

    #TODO REMOVE THIS FIELD repository (TO CLIENT)
    repository = models.TextField(
        unicode(_("repository definition")),
        null=True,
        blank=True,
        help_text=unicode(_("Define the content of source list file of repositories for the client."))
    )

    info = models.TextField(
        unicode(_("package information")),
        null=True,
        blank=True,
        help_text=unicode(_("Code bash. Define how get info of packages in the server"))
    )

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.createrepo = self.createrepo.replace("\r\n", "\n")
        self.repository = self.repository.replace("\r\n", "\n")
        self.info = self.info.replace("\r\n", "\n")
        super(Pms, self).save(*args, **kwargs) # Call the "real" save() method

    class Meta:
        verbose_name = unicode(_("Package Management System"))
        verbose_name_plural = unicode(_("Package Management Systems"))
        permissions = (("can_save_pms", "Can save Package Management System"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class Property(models.Model):
    KIND_CHOICES = (
        ('N', unicode(_('NORMAL'))),
        ('-', unicode(_('LIST'))),
        ('L', unicode(_('ADDS LEFT'))),
        ('R', unicode(_('ADDS RIGHT'))),
    )

    prefix = models.CharField(
        unicode(_("prefix")),
        max_length=3,
        unique=True
    )

    name = models.CharField(
        unicode(_("name")),
        max_length=50
    )

    language = models.IntegerField(
        unicode(_("programming language")),
        default=0,
        choices=LANGUAGES_CHOICES
    )

    code = models.TextField(
        unicode(_("Code")),
        null=False,
        blank=True,
        help_text=unicode(_("This code will execute in the client computer, and it must put in the standard output the value of the attribute correspondent to this property.<br>The format of this value is 'name~description', where 'description' is optional.<br><b>Example of code:</b><br>#Create a attribute with the name of computer from bash<br> echo $HOSTNAME"))
    )

    before_insert = models.TextField(
        unicode(_("before insert")),
        null=False,
        blank=True,
        help_text=unicode(_("Code django. This code will execute before insert the attribute in the server. You can modify the value of attribute here, using the variable 'data'."))
    )

    after_insert = models.TextField(
        unicode(_("after insert")),
        null=False,
        blank=True,
        help_text=unicode(_("Code django. This code will execute after insert the attribute in the server."))
    )

    active = models.BooleanField(
        unicode(_("active")),
        default=True,
        help_text=""
    )

    kind = models.CharField(
        unicode(_("kind")),
        max_length=1,
        default="N",
        choices=KIND_CHOICES
    )

    auto = models.BooleanField(
        unicode(_("auto")),
        default=True,
        help_text="automatically add the attribute to database"
    )

    def namefunction(self):
        return "PROPERTY_%s" % self.prefix

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.code = self.code.replace("\r\n", "\n")
        self.before_insert = self.before_insert.replace("\r\n", "\n")
        self.after_insert = self.after_insert.replace("\r\n", "\n")
        super(Property, self).save(*args, **kwargs) # Call the "real" save() method

    class Meta:
        verbose_name = unicode(_("Property"))
        verbose_name_plural = unicode(_("Properties"))
        permissions = (("can_save_property", "Can save Property"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class Version(models.Model):
    """
    Version of S.O. by example 'Ubuntu natty 32bit' or 'AZLinux-2'
    This is 'your distribution', a set of computers with a determinate Distribution for personalize.
    """
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        unique=True
    )

    pms = models.ForeignKey(
        Pms,
        verbose_name=unicode(_("package management system"))
    )

    computerbase = models.CharField(
        unicode(_("Actual line computer")),
        max_length=50,
        help_text=unicode(_("Computer with the actual line software")),
        default="---"
    )

    base = models.TextField(
        unicode(_("Actual line packages")),
        null=False,
        blank=True,
        help_text=unicode(_("List ordered of packages of actual line computer"))
    )

    autoregister = models.BooleanField(
        unicode(_("autoregister")),
        default=False,
        help_text="Is not neccesary a user for register the computer in database and get the keys."
    )
    
    platform = models.IntegerField(
        unicode(_("platform")),
        default=0,
        choices=PLATFORM_CHOICES
    )


    def __unicode__(self):
        return self.name

    def create_dirs(self):
        _repos = os.path.join(MIGASFREE_REPO_DIR, self.name, 'REPOSITORIES')
        if not os.path.exists(_repos):
            os.makedirs(_repos)

        _stores = os.path.join(MIGASFREE_REPO_DIR, self.name, 'STORES')
        if not os.path.exists(_stores):
            os.makedirs(_stores)

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "-")
        self.create_dirs()
        self.base = self.base.replace("\r\n", "\n")
        super(Version, self).save( *args, **kwargs) # Call the "real" save() method

    def delete(self, *args, **kwargs):
        # remove the directory of this version
        _path = os.path.join(MIGASFREE_REPO_DIR, self.name)
        os.system("rm -rf %s" % _path)
        super(Version, self).delete(*args, **kwargs) # Call the real delete() method

    class Meta:
        verbose_name = unicode(_("Version"))
        verbose_name_plural = unicode(_("Versions"))
        permissions = (("can_save_version", "Can save Version"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class Attribute(models.Model):
    property_att = models.ForeignKey(
        Property,
        verbose_name=unicode(_("Property of attribute"))
    )

    value = models.CharField(
        unicode(_("value")),
        max_length=250
    )

    description = models.TextField(
        unicode(_("description")),
        null=True,
        blank=True
    )

    def property_link(self):
        return self.property_att.link()

    property_link.allow_tags = True
    property_link.short_description = unicode(_("Property"))

    def __unicode__(self):
        return '%s-%s %s' % (
            self.property_att.prefix,
            self.value,
            self.description
        )

    class Meta:
        verbose_name = unicode(_("Attribute"))
        verbose_name_plural = unicode(_("Attributes"))
        unique_together = (("property_att", "value"),)
        permissions = (("can_save_attribute", "Can save Attribute"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

# ---- device.py ----

def load_devices(jsonfile):
    with open(jsonfile, "r") as f:
        data = json.load(f)

    o_devicetype = DeviceType.objects.get(name="PRINTER")

    for e in data:
        if "Net" in e:
            net = e["Net"]

        if "Local" in e:
            local = e["Local"]

    # NET
    for e in net:
        if "Computers" in e:
            computers = e["Computers"]
        if "Devices" in e:
            devices = e["Devices"]

    #Save Devices
    for device in devices:
        if device != "":
            o_devicemodel = DeviceModel.objects.get(name=device["model"])
            o_deviceconnection = DeviceConnection.objects.get(
                name=device["port"],
                devicetype=o_devicetype
            )

            try:
#                o_device=Device.objects.get(name=device["name"],connection=o_deviceconnection)
                o_device = Device.objects.get(name=device["name"])
            except:
                o_device = Device()

            o_device.name = device["name"]
            o_device.model = o_devicemodel
            o_device.connection = o_deviceconnection
            o_device.values = "_IP='"+device["IP"]+"'\n_LOCATION='"+device["location"]+"'\n"
            o_device.save()

        #Save Computers
        for computer in computers.split(","):
            if computer != "":
                try:
                    o_computer = Computer.objects.get(name=computer)
                except:
                    o_computer = Computer()
                    o_computer.name = computer
                    o_computer.dateinput = time.strftime("%Y-%m-%d")
                    o_computer.version = Version(id=1)
                    o_computer.save()

                o_computer.devices.add(o_device.id)
                o_computer.save()

    # LOCAL
    for e in local:
        o_devicemodel = DeviceModel.objects.get(name=e["model"])
        o_deviceconnection = DeviceConnection.objects.get(
            name=e["port"],
            devicetype=o_devicetype
        )

        try:
#            o_device=Device.objects.get(name=e["name"],connection=o_deviceconnection)
            o_device = Device.objects.get(name=e["name"])
        except:
            o_device = Device()

        o_device.name = e["name"]
        o_device.model = o_devicemodel
        o_device.connection = o_deviceconnection

        o_device.save()

        try:
            o_computer = Computer.objects.get(name=e["computer"])
        except:
            o_computer = Computer()
            o_computer.name = e["computer"]
            o_computer.dateinput = time.strftime("%Y-%m-%d")
            o_computer.version = Version(id=1)
            o_computer.save()

        o_computer.devices.add(o_device.id)
        o_computer.save()

    return "" # ???

class DeviceType(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = unicode(_("Device (Type)"))
        verbose_name_plural = unicode(_("Device (Types)"))
        permissions = (("can_save_devicetype", "Can save Device Type"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class DeviceManufacturer(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = unicode(_("Device (Manufacturer)"))
        verbose_name_plural = unicode(_("Device (Manufacturers)"))
        permissions = (("can_save_devicemanufacturer", "Can save Device Manufacturer"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class DeviceConnection(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        null=True,
        blank=True
    )

    fields = models.CharField(
        unicode(_("fields")),
        max_length=50,
        null=True,
        blank=True
    ) #DEPRECATED

    uri = models.CharField(
        unicode(_("uri")),
        max_length=50,
        null=True,
        blank=True
    )

    install = models.TextField(
        unicode(_("install")),
        null=True,
        blank=True,
        help_text="install"
    ) #DEPRECATED

    remove = models.TextField(
        unicode(_("remove")),
        null=True,
        blank=True,
        help_text="remove"
    ) #DEPRECATED

    devicetype = models.ForeignKey(
        DeviceType,
        verbose_name=unicode(_("device type"))
    )

    def __unicode__(self):
        return u'(%s) %s' % (self.devicetype.name, self.name)

    def save(self, *args, **kwargs):
        self.install = self.install.replace("\r\n","\n")
        self.remove = self.remove.replace("\r\n","\n")
        super(DeviceConnection, self).save(*args, **kwargs) # Call the "real" save() method

    class Meta:
        verbose_name = unicode(_("Device (Connection)"))
        verbose_name_plural = unicode(_("Device (Connections)"))
        unique_together = (("devicetype", "name"),)
        permissions = (("can_save_deviceconnection", "Can save Device Connection"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class DeviceFile(models.Model):
    name = models.FileField(upload_to="devices")

    def __unicode__(self):
        return u'%s' % (str(self.name).split("/")[-1])

    class Meta:
        verbose_name = unicode(_("Device (File)"))
        verbose_name_plural = unicode(_("Device (Files)"))
        permissions = (("can_save_devicefile", "Can save Device File"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class DeviceModel(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        null=True,
        blank=True
    )

    manufacturer = models.ForeignKey(
        DeviceManufacturer,
        verbose_name=unicode(_("manufacturer"))
    )

    devicetype = models.ForeignKey(
        DeviceType,
        verbose_name=unicode(_("type"))
    )

    devicefile = models.ForeignKey(
        DeviceFile,
        null=True,
        blank=True,
        verbose_name=unicode(_("file"))
    )

    connections = models.ManyToManyField(
        DeviceConnection,
        null=True,
        blank=True,
        verbose_name=unicode(_("connections"))
    )

    preinstall = models.TextField(
        unicode(_("pre-install")),
        null=True,
        blank=True,
        help_text="pre-install"
    )

    postinstall = models.TextField(
        unicode(_("post-install")),
        null=True,
        blank=True,
        help_text="post-install"
    )

    preremove = models.TextField(
        unicode(_("pre-remove")),
        null=True,
        blank=True,
        help_text="pre-remove"
    )

    postremove = models.TextField(
        unicode(_("post-remove")),
        null=True,
        blank=True,
        help_text="post-remove"
    )

    def __unicode__(self):
        return u'%s-%s' % (str(self.manufacturer), str(self.name))

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "_")
        self.preinstall = self.preinstall.replace("\r\n", "\n")
        self.postinstall = self.postinstall.replace("\r\n", "\n")
        self.preremove = self.preremove.replace("\r\n", "\n")
        self.postremove = self.postremove.replace("\r\n", "\n")
        super(DeviceModel, self).save(*args, **kwargs) # Call the "real" save() method

    class Meta:
        verbose_name = unicode(_("Device (Model)"))
        verbose_name_plural = unicode(_("Device (Models)"))
        unique_together = (("devicetype", "manufacturer", "name"),)
        permissions = (("can_save_devicemodel", "Can save Device Model"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class Device(models.Model):

    def device_connection_name(self):
        return ("%s" % (self.connection.name))

    device_connection_name.short_description = unicode(_('Port'))

    def device_connection_type(self):
        return ("%s" % (self.connection.devicetype.name))

    device_connection_type.short_description = unicode(_('Type'))

    def device_manufacturer_name(self):
        return ("%s" % (self.model.manufacturer.name))

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
            ret = ret + c.link() + " "
        return ret

    computers_link.allow_tags = True
    computers_link.short_description = unicode(_("Computers"))

    def fullname(self):
        if self.alias == "":
            return self.model.manufacturer.name+"-"+self.model.name+"_["+self.name+"]"
        else:
            return self.alias+"_["+self.name+"]"

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

    def render_install(self): #DEPRECATED
        ret = self.values+"\n"

        #Spaces in device name is not allowed.
        ret = ret+"_NAME=`echo $_NAME|sed \"s/ /_/g\"`\n"

        #codes
        ret = ret+self.model.preinstall+"\n"
        ret = ret+self.connection.install+"\n"
        ret = ret+self.model.postinstall+"\n"

        #replaces
        ret = ret.replace("$_FILE", "/tmp/migasfree/"+str(self.model.devicefile.name))
        ret = ret.replace("$_NUMBER", self.name)
        ret = ret.replace("$_DEVICETYPE", self.connection.devicetype.name)
        ret = ret.replace("$_MANUFACTURER", self.model.manufacturer.name)
        ret = ret.replace("$_MODEL", self.model.name)
        ret = ret.replace("$_PORT", self.connection.name)

        return ret

    def render_remove(self): #DEPRECATED
        ret = self.values+"\n"

        #Spaces in device name is not allowed.
        ret = ret+"_NAME=`echo $_NAME|sed \"s/ /_/g\"`\n"

        #codes
        ret = ret+self.model.preremove+"\n"
        ret = ret+self.connection.remove+"\n"
        ret = ret+self.model.postremove+"\n"

        #replaces
        ret = ret.replace("$_FILE", "/tmp/migasfree/"+str(self.model.devicefile.name))
        ret = ret.replace("$_NUMBER", self.name)
        ret = ret.replace("$_DEVICETYPE", self.connection.devicetype.name)
        ret = ret.replace("$_MANUFACTURER", self.model.manufacturer.name)
        ret = ret.replace("$_MODEL", self.model.name)
        ret = ret.replace("$_PORT", self.connection.name)
        return ret

    def save(self, *args, **kwargs):

#        if self.values == None or self.values == "":
#            self.values=""
#            for p in self.connection.fields.split(" "):
#                self.values=self.values+"_"+p+"=''\n"
#        self.values=self.values.replace("\r\n","\n")

        if self.uri == None or self.uri == "":
            self.uri = self.connection.uri

        super(Device, self).save(*args, **kwargs) # Call the "real" save() method
        for computer in self.computer_set.all():
            #remove the device in devices_copy
            computer.devices_modified = True
            computer.save()

    def __unicode__(self):
        return u'%s-%s-%s' % (self.name, self.model.name, self.connection.name)

    class Meta:
        verbose_name = unicode(_("Device"))
        verbose_name_plural = unicode(_("Devices"))
        unique_together = (("connection", "name"),)
        permissions = (("can_save_device", "Can save Device"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

# ---- computer.py ----

class Computer(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    version = models.ForeignKey(
        Version,
        verbose_name=unicode(_("version"))
    )

    dateinput = models.DateField(
        unicode(_("date input")),
        help_text=unicode(_("Date of input of Computer in migasfree system"))
    )

    ip = models.CharField(
        unicode(_("ip")),
        max_length=50,
        null=True,
        blank=True
    )

    software = models.TextField(
        unicode(_("software inventory")),
        null=True,
        blank=True,
        help_text=unicode(_("differences of packages respect the software base of the version"))
    )

    history_sw = models.TextField(
        unicode(_("software history")),
        default="",
        null=True,
        blank=True
    )

    devices = models.ManyToManyField(
        Device,
        null=True,
        blank=True,
        verbose_name=unicode(_("devices"))
    )

    devices_copy = models.TextField(
        unicode(_("devices_copy")),
        null=True,
        blank=False,
        editable=False
    )

    devices_modified = models.BooleanField(
        unicode(_("devices modified")),
        default=False,
        editable=False
    ) # used to "createrepositories"

    datelastupdate = models.DateTimeField(
        unicode(_("last update")),
        null=True,
        help_text=unicode(_("last update date"))
    )


    def last_login(self):
        qry = Login.objects.filter(Q(computer__id=self.id)).order_by('-date')
        if qry.count() == 0:
            return Login()
        else:
            return qry[0]

    def last_update(self):
        qry = Update.objects.filter(Q(computer__id=self.id)).order_by('-date')
        if qry.count() == 0:
            return Update()
        else:
            return qry[0]

    def login_link(self):
        return self.last_login().link()

    login_link.allow_tags = True
    login_link.short_description = unicode(_("Last login"))

    def update_link(self):
        return self.last_update().link()

    update_link.allow_tags = True
    update_link.short_description = unicode(_("Last update"))

    def hw_link(self):
        node = HwNode.objects.get(computer=self.id, parent=None)
        return '<a href="%s">%s</a>' % (
            "/migasfree/hardware_resume/" + str(self.id),
            node.product
        )

    hw_link.allow_tags = True
    hw_link.short_description = unicode(_("Hardware"))

    def devices_link(self):
        ret = ""
        for dev in self.devices.all():
            ret = ret + dev.link() + " "

        return ret

    devices_link.allow_tags = True
    devices_link.short_description = unicode(_("Devices"))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = unicode(_("Computer"))
        verbose_name_plural = unicode(_("Computers"))
        permissions = (("can_save_computer", "Can save Computer"),)

    def link(self): #for be used with firessh
        return '<a href="%s"><img src="/repo/icons/terminal.png" height="16px" alt="ssh" /></a> <a href="%s">%s</a>' % (
            "ssh://root@%s" % str(self.ip),
            ADMIN_SITE_ROOT_URL + "server/computer/" + str(self.id),
            self.name
        )

    link.allow_tags = True
    link.short_description = Meta.verbose_name

class MessageServer(models.Model):

    text = models.CharField(
        unicode(_("text")),
        max_length=100,
        null=True,
        blank=True
    )

    date = models.DateTimeField(
        unicode(_("date")),
        default=0
    )

    def __unicode__(self):
        return '%s' % (self.text)

    class Meta:
        verbose_name = unicode(_("Message Server"))
        verbose_name_plural = unicode(_("Messages Server"))
        permissions = (("can_save_messageserver", "Can save Message Server"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True



class Message(models.Model):
    computer = models.ForeignKey(
        Computer,
        verbose_name=unicode(_("computer")),
        unique=True
    )

    text = models.CharField(
        unicode(_("text")),
        max_length=100,
        null=True,
        blank=True
    )

    date = models.DateTimeField(
        unicode(_("date")),
        default=0
    )

    def __unicode__(self):
        return '%s - %s' % (self.computer.name, self.text)

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = unicode(_("Computer"))

    class Meta:
        verbose_name = unicode(_("Message"))
        verbose_name_plural = unicode(_("Messages"))
        permissions = (("can_save_message", "Can save Message"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class Update(models.Model):
    computer = models.ForeignKey(
        Computer,
        verbose_name=unicode(_("computer"))
    )

    version = models.ForeignKey(
        Version,
        verbose_name=unicode(_("version")),
        null=True
    )

    date = models.DateTimeField(
        unicode(_("date")),
        default=0
    )

    def __unicode__(self):
        return '%s-%s' % (self.computer.name, self.date)

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = unicode(_("Computer"))

    class Meta:
        verbose_name = unicode(_("Update"))
        verbose_name_plural = unicode(_("Updates"))
        permissions = (("can_save_update", "Can save Update"),)

    def save(self, *args, **kwargs):
        super(Update, self).save(*args, **kwargs)

        #update last update in computer
        self.computer.datelastupdate=self.date
        self.computer.save()




    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class Error(models.Model):
    computer = models.ForeignKey(
        Computer,
        verbose_name=unicode(_("computer"))
    )

    date = models.DateTimeField(
        unicode(_("date")),
        default=0
    )

    error = models.TextField(
        unicode(_("error")),
        null=True,
        blank=True
    )

    checked = models.BooleanField(
        unicode(_("checked")),
        default=False,
        help_text=""
    )

    def auto_check(self):
        msg = self.error
        for ace in AutoCheckError.objects.all():
            msg = msg.replace(ace.message, "")

        msg = msg.replace("\n", "")
        if msg == "":
            self.checked = True

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = unicode(_("Computer"))

    def save(self, *args, **kwargs):
        self.error = self.error.replace("\r\n", "\n")
        self.auto_check()
        super(Error, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s - %s - %s' % (
            str(self.id),
            self.computer.name,
            str(self.date)
        )

    class Meta:
        verbose_name = unicode(_("Error"))
        verbose_name_plural = unicode(_("Errors"))
        permissions = (("can_save_error", "Can save Error"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class Login(models.Model):
    date = models.DateTimeField(
        unicode(_("date")),
        default=0
    )

    computer = models.ForeignKey(
        Computer,
        verbose_name=unicode(_("computer"))
    )

    user = models.ForeignKey(
        User,
        verbose_name=unicode(_("user"))
    )

    attributes = models.ManyToManyField(
        Attribute,
        null=True,
        blank=True,
        verbose_name=unicode(_("attributes")),
        help_text=_("Sent attributes")
    )

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = unicode(_("Computer"))

    def user_link(self):
        return self.user.link()

    user_link.allow_tags = True
    user_link.short_description = unicode(_("User"))

    def __unicode__(self):
        return '%s@%s' % (
            self.user.name,
            self.computer.name
        )

    class Meta:
        verbose_name = unicode(_("Login"))
        verbose_name_plural = unicode(_("Logins"))
        unique_together = (("computer", "user"),)
        permissions = (("can_save_login", "Can save Login"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

# ---- fault.py ----

class FaultDef(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        unique=True
    )

    description = models.TextField(
        unicode(_("description")),
        null=True,
        blank=True
    )

    active = models.BooleanField(
        unicode(_("active")),
        default=True
    )

    language = models.IntegerField(
        unicode(_("programming language")),
        default=0,
        choices=LANGUAGES_CHOICES
    )

    code = models.TextField(
        unicode(_("Code")),
        null=False,
        blank=True
    )

    attributes = models.ManyToManyField(
        Attribute,
        null=True,
        blank=True,
        verbose_name=unicode(_("attributes"))
    )

    def list_attributes(self):
        cattributes = ""
        for i in self.attributes.all():
            cattributes = cattributes + i.value + ","

        return cattributes[0:len(cattributes) - 1]

    list_attributes.short_description = unicode(_("attributes"))

    def save(self, *args, **kwargs):
        self.code = self.code.replace("\r\n", "\n")
        self.name = self.name.replace(" ", "_")
        super(FaultDef, self).save(*args, **kwargs)

    def namefunction(self):
        return "FAULT_%s" % self.name

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = unicode(_("Fault Definition"))
        verbose_name_plural = unicode(_("Faults Definition"))
        permissions = (("can_save_faultdef", "Can save Fault Definition"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class Fault(models.Model):
    computer = models.ForeignKey(
        Computer,
        verbose_name=unicode(_("computer"))
    )

    faultdef = models.ForeignKey(
        FaultDef,
        verbose_name=unicode(_("fault definition"))
    )

    date = models.DateTimeField(
        unicode(_("date")),
        default=0
    )

    text = models.TextField(
        unicode(_("text")),
        null=True,
        blank=True
    )

    checked = models.BooleanField(
        unicode(_("checked")),
        default=False,
        help_text=""
    )

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = unicode(_("Computer"))

    def __unicode__(self):
        return '%s - %s - %s' % (
            str(self.id),
            self.computer.name,
            str(self.date)
        )

    class Meta:
        verbose_name = unicode(_("Fault"))
        verbose_name_plural = unicode(_("Faults"))
        permissions = (("can_save_fault", "Can save Fault"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

# ---- hardware.py ----

def load_hw(computer, node, parent, level):
    n = HwNode()
    n.parent = parent
    n.computer = computer
    n.level = level
    n.name = str(node["id"])
    n.classname = node["class"]
    if "enabled" in node:
        n.enabled = node["enabled"]
    if "claimed" in node:
        n.claimed = node["claimed"]
    if "description" in node:
        n.description = node["description"]
    if "vendor" in node:
        n.vendor = node["vendor"]
    if "product" in node:
        n.product = node["product"]
    if "version" in node:
        n.version = node["version"]
    if "serial" in node:
        n.serial = node["serial"]
    if "businfo" in node:
        n.businfo = node["businfo"]
    if "physid" in node:
        n.physid = node["physid"]
    if "slot" in node:
        n.slot = node["slot"]
    if "size" in node:
        n.size = int(node["size"])
    if "capacity" in node:
        n.capacity = node["capacity"]
    if "clock" in node:
        n.clock = node["clock"]
    if "width" in node:
        n.width = node["width"]
    if "dev" in node:
        n.dev = node["dev"]

    #set icons
    if not n.product == None:
        if n.classname == "system" and n.product == "VirtualBox ()":
            n.icon = "virtualbox.png"

        if n.classname == "system" and n.product == "VMware Virtual Platform ()":
            n.icon = "vmplayer.png"

    if not n.businfo == None:
        if n.classname == "processor" and "cpu@" in n.businfo:
            n.icon = "cpu.png"

    if n.classname == "display":
        n.icon = "display.png"

    if not n.description == None:
#    if n.classname=="system" and n.description.lower() in ["notebook",]:
#      n.icon="laptop.png"

        if n.classname == "memory" and n.description.lower() == "system memory":
            n.icon = "memory.png"

        if n.classname == "bus" and n.description.lower() == "motherboard":
            n.icon = "motherboard.png"

        if n.classname == "memory" and n.description.lower() == "bios":
            n.icon = "chip.png"

        if n.classname == "network" and n.description.lower() == "ethernet interface":
            n.icon = "network.png"

        if n.classname == "network" and n.description.lower() == "wireless interface":
            n.icon = "radio.png"

        if n.classname == "multimedia" and n.description.lower() in ["audio device", "multimedia audio controller", ]:
            n.icon = "audio.png"

        if n.classname == "bus" and n.description.lower() == "smbus":
            n.icon = "serial.png"

        if n.classname == "bus" and n.description.lower() == "usb controller":
            n.icon = "usb.png"

        if not n.name == None:
            if n.classname == "disk" and n.name.lower() == "disk":
                n.icon = "disc.png"

            if n.classname == "disk" and n.name.lower() == "cdrom":
                n.icon = "cd.png"

        if n.classname == "power" and n.name.lower() == "battery":
            n.icon = "battery.png"

        if n.classname == "storage" and n.name.lower() == "scsi":
            n.icon = "scsi.png"

    n.save()
    level = level+3

    for e in node:
        if e == "children":
            for x in node[e]:
                load_hw(computer, x, n, level)
        elif e == "capabilities":
            for x in node[e]:
                c = HwCapability()
                c.node = n
                c.name = x
                c.description = node[e][x]
                c.save()
        elif e == "configuration":
            for x in node[e]:
                c = HwConfiguration()
                c.node = n
                c.name = x
                c.value = node[e][x]
                c.save()
        elif e == "logicalname":
            if type(node[e]) == unicode:
                c = HwLogicalName()
                c.node = n
                c.name = node[e]
                c.save()
            else:
                for x in node[e]:
                    c = HwLogicalName()
                    c.node = n
                    c.name = x
                    c.save()
        elif e == "resource":
            print e, node[e]
        else:
            pass

    if n.classname == "system":
        try:
            chassis = HwConfiguration.objects.get(name="chassis", node__id=n.id)
            chassisname = chassis.value.lower()
            if chassisname == "notebook":
                n.icon = "laptop.png"

            if chassisname == "low-profile":
                n.icon = "desktopcomputer.png"

            if chassisname == "mini-tower":
                n.icon = "towercomputer.png"

            n.save()

        except:
            pass

    return # ???

def process_hw(computer, jsonfile):
    with open(jsonfile, "r") as f:
        data = json.load(f)

    HwNode.objects.filter(computer=computer).delete()
    load_hw(computer, data, None, 1)

    return # ???

class HwNode(models.Model):
    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        verbose_name=unicode(_("parent")),
        related_name="child"
    )

    level = width = models.IntegerField(
        unicode(_("width")),
        null=False
    )

    width = models.IntegerField(
        unicode(_("width")),
        null=True
    )

    computer = models.ForeignKey(
        Computer,
        verbose_name=unicode(_("computer"))
    )

    name = models.TextField(
        unicode(_("id")),
        null=False,
        blank=True
    ) # This is the field "id" in lshw

    classname = models.TextField(
        unicode(_("class")),
        null=False,
        blank=True
    ) # This is the field "class" in lshw

    enabled = models.BooleanField(
        unicode(_("enabled")),
        default=False,
        help_text=""
    )

    claimed = models.BooleanField(
        unicode(_("claimed")),
        default=False,
        help_text=""
    )

    description = models.TextField(
        unicode(_("description")),
        null=True,
        blank=True
    )

    vendor = models.TextField(
        unicode(_("vendor")),
        null=True,
        blank=True
    )

    product = models.TextField(
        unicode(_("product")),
        null=True,
        blank=True
    )

    version = models.TextField(
        unicode(_("version")),
        null=True,
        blank=True
    )

    serial = models.TextField(
        unicode(_("serial")),
        null=True,
        blank=True
    )

    businfo = models.TextField(
        unicode(_("businfo")),
        null=True,
        blank=True
    )

    physid = models.TextField(
        unicode(_("physid")),
        null=True,
        blank=True
    )

    slot = models.TextField(
        unicode(_("slot")),
        null=True,
        blank=True
    )

    size = models.BigIntegerField(
        unicode(_("size")),
        null=True
    )

    capacity = models.BigIntegerField(
        unicode(_("capacity")),
        null=True
    )

    clock = models.IntegerField(
        unicode(_("clock")),
        null=True
    )

    dev = models.TextField(
        unicode(_("dev")),
        null=True,
        blank=True
    )

    icon = models.TextField(
        unicode(_("icon")),
        null=True,
        blank=True
    )

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = unicode(_("Hardware Node"))
        verbose_name_plural = unicode(_("Hardware Nodes"))

class HwCapability(models.Model):
    node = models.ForeignKey(
        HwNode,
        verbose_name=unicode(_("hardware node"))
    )

    name = models.TextField(
        unicode(_("name")),
        null=False,
        blank=True
    ) # This is the field "capability" in lshw

    description = models.TextField(
        unicode(_("description")),
        null=True,
        blank=True
    )

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = unicode(_("Hardware Capability"))
        verbose_name_plural = unicode(_("Hardware Capabilities"))
        unique_together = (("name", "node"),)

class HwConfiguration(models.Model):
    node = models.ForeignKey(
        HwNode,
        verbose_name=unicode(_("hardware node"))
    )

    name = models.TextField(
        unicode(_("name")),
        null=False,
        blank=True
    ) # This is the field "config" in lshw

    value = models.TextField(
        unicode(_("value")),
        null=True,
        blank=True
    )

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = unicode(_("Hardware Capability"))
        verbose_name_plural = unicode(_("Hardware Capabilities"))
        unique_together = (("name", "node"),)

class HwLogicalName(models.Model):
    node = models.ForeignKey(
        HwNode,
        verbose_name=unicode(_("hardware node"))
    )

    name = models.TextField(
        unicode(_("name")),
        null=False,
        blank=True
    ) # This is the field "logicalname" in lshw

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = unicode(_("Hardware Logical Name"))
        verbose_name_plural = unicode(_("Hardware Logical Names"))

# ---- schedule.py ----

class Schedule(models.Model):
    name = models.CharField(
        unicode(_("name")),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    description = models.TextField(
        unicode(_("description")),
        null=True,
        blank=True
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = unicode(_("Schedule"))
        verbose_name_plural = unicode(_("Schedules"))
        permissions = (("can_save_schedule", "Can save Schedule"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class ScheduleDelay(models.Model):
    delay = models.IntegerField(unicode(_("delay")))

    schedule = models.ForeignKey(
        Schedule,
        verbose_name=unicode(_("schedule"))
    )

    attributes = models.ManyToManyField(
        Attribute,
        null=True,
        blank=True,
        verbose_name=unicode(_("attributes"))
    )

    def __unicode__(self):
#        return '%s - %s' % (str(self.delay), self.schedule.name)
        return ''

    def list_attributes(self):
        cattributes = ""
        for i in self.attributes.all():
            cattributes = cattributes + i.value + ","

        return cattributes[0:len(cattributes) - 1]

    list_attributes.short_description = unicode(_("attributes"))

    class Meta:
        verbose_name = unicode(_("Schedule Delay"))
        verbose_name_plural = unicode(_("Schedule Delays"))
        unique_together = (("schedule", "delay"),)
        permissions = (("can_save_scheduledelay", "Can save Schedule Delay"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

# ---- repository.py ----

class Store(models.Model):
    """
    Ubicacion: rutas donde se guardaran los paquetes. P.e. /terceros/vmware
    """
    name = models.CharField(
        unicode(_("name")),
        max_length=50
    )

    version = models.ForeignKey(
        Version,
        verbose_name=unicode(_("version"))
    )

    objects = VersionManager() # manager by user version

    def create_dir(self):
        _path = os.path.join(
            MIGASFREE_REPO_DIR,
            self.version.name,
            'STORES',
            self.name
        )
        if not os.path.exists(_path):
            os.makedirs(_path)

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "-")
        self.create_dir()
        super(Store, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # remove the directory of Store
        _path = os.path.join(
            MIGASFREE_REPO_DIR,
            self.version.name,
            "STORES",
            self.name
        )
        os.system("rm -rf %s" % _path)
        super(Store, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta():
        verbose_name = unicode(_("Store"))
        verbose_name_plural = unicode(_("Stores"))
        unique_together = (("name", "version"),)
        permissions = (("can_save_store", "Can save Store"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class Package(models.Model):
    "Package:"
    name = models.CharField(
        unicode(_("name")),
        max_length=100
    )

    version = models.ForeignKey(
        Version,
        verbose_name=unicode(_("version"))
    )

    store = models.ForeignKey(
        Store,
        verbose_name=unicode(_("store"))
    )

    objects = VersionManager() # manager by user version

    def create_dir(self):
        _path = os.path.join(
            MIGASFREE_REPO_DIR,
            self.version.name,
            'STORES',
            self.store.name,
            self.name
        )
        if not os.path.exists(_path):
            os.makedirs(_path)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = unicode(_("Package/Set"))
        verbose_name_plural = unicode(_("Packages/Sets"))
        unique_together = (("name", "version"),)
        permissions = (("can_save_package", "Can save Package"),)

    def link(self):
        info = "/migasfree/info/STORES/%s/%s/?version=%s" % (self.store.name, self.name, self.version.name)


        return '<a href="%s"><img src="/repo/icons/package-info.png" height="16px" alt="information" /></a> <a href="%s">%s</a>' % (
            info,
            ADMIN_SITE_ROOT_URL + "server/package/" + str(self.id),
            self.__unicode__()
        )

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class Repository(models.Model):
    "Repository:"

    name = models.CharField(
        unicode(_("name")),
        max_length=50
    )

    version = models.ForeignKey(
        Version,
        verbose_name=unicode(_("version"))
    )

    packages = models.ManyToManyField(
        Package,
        null=True,
        blank=True,
        verbose_name=unicode(_("Packages/Set")),
        help_text="Assigned Packages"
    )

    attributes = models.ManyToManyField(
        Attribute,
        null=True,
        blank=True,
        verbose_name=unicode(_("attributes")),
        help_text="Assigned Attributes"
    )

    excludes = models.ManyToManyField(
        Attribute,
        related_name="ExcludeAttribute",
        null=True,
        blank=True,
        verbose_name=unicode(_("excludes")),
        help_text="Excluded Attributes"
    )

    schedule = models.ForeignKey(
        Schedule,
        null=True,
        blank=True,
        verbose_name=unicode(_("schedule"))
    )

    createpackages = models.ManyToManyField(
        Package,
        null=True,
        blank=True,
        verbose_name=unicode(_("createpackages")),
        related_name="createpackages",
        editable=False
    ) # used to know when "createrepositories"

    active = models.BooleanField(
        unicode(_("active")),
        default=True,
        help_text=unicode(_("if you uncheck this field, the repository is hidden for all computers."))
    )

    date = models.DateField(
        unicode(_("date")),
        help_text=unicode(_("Date initial for distribute."))
    )

    comment = models.TextField(
        unicode(_("comment")),
        null=True,
        blank=True
    )

    toinstall = models.TextField(
        unicode(_("packages to install")),
        null=True,
        blank=True
    )

    toremove = models.TextField(
        unicode(_("packages to remove")),
        null=True,
        blank=True
    )

    modified = models.BooleanField(
        unicode(_("modified")),
        default=False,
        editable=False
    ) # used to "createrepositories"

    objects = VersionManager() # manager by user version

    def packages_link(self):
        ret = ""
        for pack in self.packages.all():
            ret = ret + pack.link() + " "

        return ret

    packages_link.allow_tags = True
    packages_link.short_description = unicode(_("Packages"))

    def __unicode__(self):
        return u'%s' % (self.name)

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "_")
        self.toinstall = self.toinstall.replace("\r\n", "\n")
        self.toremove = self.toremove.replace("\r\n", "\n")
        super(Repository, self).save(*args, **kwargs) # Call the "real" save() method

    def delete(self, *args, **kwargs):
        # remove the directory of repository
        _path = os.path.join(
            MIGASFREE_REPO_DIR,
            self.version.name,
            self.version.pms.slug,
            self.name
        )
        os.system("rm -rf %s" % _path)
        super(Repository, self).delete(*args, **kwargs) # Call the real delete() method

    def timeline(self):
        ret = "<table class=\"\">"
        delays = ScheduleDelay.objects.filter(schedule__id=self.schedule.id).order_by('delay')

        for d in delays:
            hori = horizon(self.date, d.delay)
            if hori <= datetime.now().date():
                ret = ret+"<tr class=\"\"><td><b>"
                l = d.attributes.values_list("value")
                ret = ret+"<b>"+hori.strftime("%a-%b-%d")+"</b></td><td><b>"
                for e in l:
                    ret = ret+e[0]+" "
                ret = ret+"</b></td></tr>"
            else:
                ret = ret+"<tr class=\"\"><td>"
                l = d.attributes.values_list("value")
                ret = ret+hori.strftime("%a-%b-%d")+"</td><td>"
                for e in l:
                    ret = ret+e[0]+" "

                ret = ret+"</td></tr>"

        return ret+"</table>"

    timeline.allow_tags = True
    timeline.short_description = unicode(_('timeline'))

    class Meta:
        verbose_name = unicode(_("Repository"))
        verbose_name_plural = unicode(_("Repositories"))
        unique_together = (("name", "version"),)
        permissions = (("can_save_repository", "Can save Repository"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True

class UserProfile(UserSystem):
    info = "For designate the password use <a href=\"/migasfree/auth/password/\">change password form</a>."

    version = models.ForeignKey(
        Version,
        verbose_name=unicode(_("version")),
        null=True
    )

    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.password.startswith("sha1$"):
            super(UserProfile, self).set_password(self.password)
        super(UserProfile, self).save(*args, **kwargs) # Call the "real" save() method

    class Meta:
        verbose_name = unicode(_("User Profile"))
        verbose_name_plural = unicode(_("Users Profile"))
        permissions = (("can_save_userprofile", "Can save User Profile"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
