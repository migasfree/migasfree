# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from migasfree.settings import STATIC_URL

from common import link
from server.models.version import Version
from server.models.device import Device
from server.models.user import User
from server.models.attribute import Attribute


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
    )  # used to "createrepositories"

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
            reverse('hardware_resume', args=(self.id, )),
            node.product
        )

    hw_link.allow_tags = True
    hw_link.short_description = unicode(_("Hardware"))

    def devices_link(self):
        ret = ""
        for dev in self.devices.all():
            ret += dev.link() + " "

        return ret

    devices_link.allow_tags = True
    devices_link.short_description = unicode(_("Devices"))

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Computer"))
        verbose_name_plural = unicode(_("Computers"))
        permissions = (("can_save_computer", "Can save Computer"),)

    def link(self):  # for be used with firessh
        return '<a href="%s"><img src="%sicons/terminal.png" height="16px" alt="ssh" /></a> <a href="%s">%s</a>' % (
            "ssh://root@%s" % str(self.ip),
            STATIC_URL,
            reverse('admin:server_computer_change', args=(self.id, )),
            self.name
        )

    link.allow_tags = True
    link.short_description = Meta.verbose_name


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
        return u'%s@%s' % (
            self.user.name,
            self.computer.name
        )

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Login"))
        verbose_name_plural = unicode(_("Logins"))
        unique_together = (("computer", "user"),)
        permissions = (("can_save_login", "Can save Login"),)

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
        return u'%s-%s' % (self.computer.name, self.date)

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = unicode(_("Computer"))

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Update"))
        verbose_name_plural = unicode(_("Updates"))
        permissions = (("can_save_update", "Can save Update"),)

    def save(self, *args, **kwargs):
        super(Update, self).save(*args, **kwargs)

        #update last update in computer
        self.computer.datelastupdate = self.date
        self.computer.save()

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True


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
    )  # This is the field "id" in lshw

    classname = models.TextField(
        unicode(_("class")),
        null=False,
        blank=True
    )  # This is the field "class" in lshw

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
        app_label = 'server'
        verbose_name = unicode(_("Hardware Node"))
        verbose_name_plural = unicode(_("Hardware Nodes"))
