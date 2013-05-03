# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.template import Context, Template

from migasfree.server.models import Version, Device, Attribute
from migasfree.settings import MIGASFREE_COMPUTER_SEARCH_FIELDS
from migasfree.settings import MIGASFREE_REMOTE_ADMIN_LINK


class Computer(models.Model):
    name = models.CharField(
        _("name"),
        max_length=50,
        null=True,
        blank=True,
        unique=False
    )  # south 0004

    uuid = models.CharField(
        _("uuid"),
        max_length=36,
        null=True,
        blank=True,
        unique=True,
        default=""
    )  # south 0003 & 0004

    version = models.ForeignKey(
        Version,
        verbose_name=_("version")
    )

    dateinput = models.DateField(
        _("date input"),
        help_text=_("Date of input of Computer in migasfree system")
    )

    ip = models.CharField(
        _("ip"),
        max_length=50,
        null=True,
        blank=True
    )

    software = models.TextField(
        _("software inventory"),
        null=True,
        blank=True,
        help_text=_("gap between software base packages and computer ones")
    )

    history_sw = models.TextField(
        _("software history"),
        default="",
        null=True,
        blank=True
    )

    devices = models.ManyToManyField(
        Device,
        null=True,
        blank=True,
        verbose_name=_("devices")
    )

    devices_copy = models.TextField(
        _("devices copy"),
        null=True,
        blank=False,
        editable=False
    )

    devices_modified = models.BooleanField(
        _("devices modified"),
        default=False,
        editable=False
    )

    datelastupdate = models.DateTimeField(
        _("last update"),
        null=True,
    )

    datehardware = models.DateTimeField(
        _("last hardware capture"),
        null=True,
        blank=True,
    )

    tags = models.ManyToManyField(
        Attribute,
        null=True,
        blank=True,
        verbose_name=_("tags")
    )

    def last_login(self):
        try:
            return self.login_set.filter(
                Q(computer__id=self.id)
            ).order_by('-date')[0]
        except:
            return None

    def last_update(self):
        try:
            return self.update_set.filter(
                Q(computer__id=self.id)
            ).order_by('-date')[0]
        except:
            return None

    def login_link(self):
        return self.last_login().link()

    login_link.allow_tags = True
    login_link.short_description = _("Last login")

    def update_link(self):
        return self.last_update().link()

    update_link.allow_tags = True
    update_link.short_description = _("Last update")

    def hw_link(self):
        return '<a href="%s">%s</a>' % (
            reverse('hardware_resume', args=(self.id, )),
            self.hwnode_set.get(computer=self.id, parent=None).product
        )

    hw_link.allow_tags = True
    hw_link.short_description = _("Hardware")

    def devices_link(self):
        ret = ""
        for dev in self.devices.all():
            ret += dev.link() + " "

        return ret

    devices_link.allow_tags = True
    devices_link.short_description = _("Devices")

    def __unicode__(self):
        return str(self.__getattribute__(MIGASFREE_COMPUTER_SEARCH_FIELDS[0]))

    class Meta:
        app_label = 'server'
        verbose_name = _("Computer")
        verbose_name_plural = _("Computers")
        permissions = (("can_save_computer", "Can save Computer"),)

    def link(self):  # to be used with FireSSH

        if MIGASFREE_REMOTE_ADMIN_LINK:
            _template = Template(MIGASFREE_REMOTE_ADMIN_LINK)
            _context = {"computer": self}
            for n in _template.nodelist:
                try:
                    _token = n.filter_expression.token
                    if not _token.startswith("computer"):
                        _context[_token] = self.last_login().attributes.get(
                            property_att__prefix=_token).value
                except:
                    pass
            _remote_admin = _template.render(Context(_context))

            return '''<a href="%s" class="ssh" title="%s">&nbsp;</a>
            <a href="%s">%s</a>''' % (
                _remote_admin,
                str(self.ip),  # _("Opens a SSH connection"),
                reverse('admin:server_computer_change', args=(self.id, )),
                self.__unicode__()
            )
        else:

            return '''<a href="%s">%s</a>''' % (
                reverse('admin:server_computer_change', args=(self.id, )),
                self.__unicode__()
            )

    link.allow_tags = True
    link.short_description = Meta.verbose_name
