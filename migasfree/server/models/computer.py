# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.template import Context, Template
from django.conf import settings

from migasfree.server.models import (
    Version, DeviceLogical, Attribute, MigasLink
)

from migasfree.server.functions import s2l, l2s


class ProductiveManager(models.Manager):
    def get_query_set(self):
        return super(ProductiveManager, self).get_queryset().filter(
            status__in=Computer.PRODUCTIVE_STATUS
        )


class UnproductiveManager(models.Manager):
    def get_query_set(self):
        return super(UnproductiveManager, self).get_queryset().exclude(
            status__in=Computer.PRODUCTIVE_STATUS
        )


class Computer(models.Model, MigasLink):
    STATUS_CHOICES = (
        ('intended', _('Intended')),
        ('reserved', _('Reserved')),
        ('unknown', _('Unknown')),
        ('in repair', _('In repair')),
        ('available', _('Available')),
        ('unsubscribed', _('Unsubscribed')),
    )

    PRODUCTIVE_STATUS = ['intended', 'reserved', 'unkown']

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

    status = models.CharField(
        verbose_name=_('status'),
        max_length=20,
        null=False,
        choices=STATUS_CHOICES,
        default='intended'
    )

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

    devices_logical = models.ManyToManyField(
        DeviceLogical,
        null=True,
        blank=True,
        verbose_name=_("devices"),
    )

    devices_copy = models.TextField(
        _("devices copy"),
        null=True,
        blank=False,
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

    def __init__(self, *args, **kwargs):
        super(Computer, self).__init__(*args, **kwargs)
        if settings.MIGASFREE_REMOTE_ADMIN_LINK == '' \
        or settings.MIGASFREE_REMOTE_ADMIN_LINK is None:
            self._actions = None

        self._actions = []
        _template = Template(settings.MIGASFREE_REMOTE_ADMIN_LINK)
        _context = {"computer": self}
        for n in _template.nodelist:
            try:
                _token = n.filter_expression.token
                if not _token.startswith("computer"):
                    attributes = self.login().attributes.filter(
                        property_att__prefix=_token
                    )
                    cad = ""
                    for attribute in attributes:
                        cad += attribute.value + ","
                    _context[_token] = cad[:-1]
            except:
                pass
        _remote_admin = _template.render(Context(_context))

        for element in _remote_admin.split(" "):
            protocol = element.split("://")[0]
            self._actions.append([protocol, element])

    def remove_device_copy(self, devicelogical_id):
        try:
            lst = s2l(self.devices_copy)
            if devicelogical_id in lst:
                lst.remove(devicelogical_id)
                self.devices_copy = l2s(lst)
                self.save()
        except:
            pass

    def append_device_copy(self, devicelogical_id):
        try:
            lst = s2l(self.devices_copy)
            if devicelogical_id not in lst:
                lst.append(devicelogical_id)
                self.devices_copy = l2s(lst)
                self.save()
        except:
            pass

    def last_update(self):
        return self.update_set.filter(
            computer__id__exact=self.id
        ).order_by('-date')[0]

    def update_link(self):
        try:
            return self.last_update().link()
        except:
            return ''

    update_link.allow_tags = True
    update_link.short_description = _("Last update")

    def login_link(self):
        try:
            return self.login().link()
        except:
            return ''

    login_link.allow_tags = True
    login_link.short_description = _("login")

    def login(self):
        return self.login_set.get(computer=self.id)

    def hw_link(self):
        try:
            return self.hwnode_set.get(computer=self.id, parent=None).link()
        except:
            return ''

    hw_link.allow_tags = True
    hw_link.short_description = _("Hardware")

    def devices_link(self):
        return ' '.join(dev.link() for dev in self.devices_logical.all())

    devices_link.allow_tags = True
    devices_link.short_description = _("Devices")

    def version_link(self):
        return self.version.link()

    version_link.allow_tags = True
    version_link.short_description = _("Version")

    def change_status(self, status):
        if status not in list(dict(self.STATUS_CHOICES).keys()):
            return False

        self.status = status
        self.save()

        return True

    @staticmethod
    def replacement(source, target):
        source.tags, target.tags = target.tags, source.tags
        source.status, target.status = target.status, source.status

        source.save()
        target.save()

    def productive(self):
        return self.status in self.PRODUCTIVE_STATUS

    def save(self, *args, **kwargs):
        if 'available' == self.status:
            self.tags.clear()

        super(Computer, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.__getattribute__(
            settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0]
        ))

    # Managers
    objects = models.Manager()
    productives = ProductiveManager()
    unproductives = UnproductiveManager()

    class Meta:
        app_label = 'server'
        verbose_name = _("Computer")
        verbose_name_plural = _("Computers")
        permissions = (("can_save_computer", "Can save Computer"),)


def computers_changed(sender, **kwargs):
    if kwargs['action'] == 'post_add':
        for computer in Computer.objects.filter(pk__in=kwargs['pk_set']):
            computer.remove_device_copy(kwargs['instance'].id)

m2m_changed.connect(computers_changed, sender=Computer.devices_logical.through)


from .status_log import StatusLog


@receiver(pre_save, sender=Computer)
def pre_save_computer(sender, instance, **kwargs):
    if instance.id:
        old_obj = Computer.objects.get(pk=instance.id)
        if old_obj.status != instance.status:
            StatusLog.objects.create(instance)

