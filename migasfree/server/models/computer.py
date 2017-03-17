# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from django.db.models.signals import pre_save, post_save
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _
from django.template import Context, Template
from django.conf import settings

from ..functions import swap_m2m, remove_empty_elements_from_dict

from . import Version, Attribute, Property, MigasLink, DeviceLogical, User


class ProductiveManager(models.Manager):
    def get_queryset(self):
        return super(ProductiveManager, self).get_queryset().filter(
            status__in=Computer.PRODUCTIVE_STATUS
        )


class UnproductiveManager(models.Manager):
    def get_queryset(self):
        return super(UnproductiveManager, self).get_queryset().exclude(
            status__in=Computer.PRODUCTIVE_STATUS
        )


class SubscribedManager(models.Manager):
    def get_queryset(self):
        return super(SubscribedManager, self).get_queryset().exclude(
            status='unsubscribed'
        )


class UnsubscribedManager(models.Manager):
    def get_queryset(self):
        return super(UnsubscribedManager, self).get_queryset().filter(
            status='unsubscribed'
        )


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(
            status__in=Computer.ACTIVE_STATUS
        )


class InactiveManager(models.Manager):
    def get_queryset(self):
        return super(InactiveManager, self).get_queryset().exclude(
            status__in=Computer.ACTIVE_STATUS
        )


class ComputerManager(models.Manager):
    def create(self, name, version, uuid, ip=None):
        obj = Computer()
        obj.name = name
        obj.version = version
        obj.uuid = uuid
        obj.ip = ip
        obj.save()

        return obj


@python_2_unicode_compatible
class Computer(models.Model, MigasLink):
    STATUS_CHOICES = (
        ('intended', _('Intended')),
        ('reserved', _('Reserved')),
        ('unknown', _('Unknown')),
        ('in repair', _('In repair')),
        ('available', _('Available')),
        ('unsubscribed', _('Unsubscribed')),
    )

    PRODUCTIVE_STATUS = ['intended', 'reserved', 'unknown']
    ACTIVE_STATUS = PRODUCTIVE_STATUS + ['in repair']

    MACHINE_CHOICES = (
        ('P', _('Physical')),
        ('V', _('Virtual')),
    )

    uuid = models.CharField(
        verbose_name=_("uuid"),
        max_length=36,
        null=True,
        blank=True,
        unique=True,
        default=""
    )

    status = models.CharField(
        verbose_name=_('status'),
        max_length=20,
        null=False,
        choices=STATUS_CHOICES,
        default=settings.MIGASFREE_DEFAULT_COMPUTER_STATUS
    )

    name = models.CharField(
        verbose_name=_("name"),
        max_length=50,
        null=True,
        blank=True,
        unique=False
    )

    version = models.ForeignKey(
        Version,
        verbose_name=_("version")
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text=_('Date of entry into the migasfree system'))
    updated_at = models.DateTimeField(auto_now=True)

    ip_address = models.CharField(
        verbose_name=_("ip address"),
        max_length=50,
        null=True,
        blank=True
    )

    software_inventory = models.TextField(
        verbose_name=_("software inventory"),
        null=True,
        blank=True,
        help_text=_("gap between software base packages and computer ones")
    )

    software_history = models.TextField(
        verbose_name=_("software history"),
        default="",
        null=True,
        blank=True
    )

    default_logical_device = models.ForeignKey(
        DeviceLogical,
        null=True,
        blank=True,
        verbose_name=_("default logical device")
    )

    last_hardware_capture = models.DateTimeField(
        verbose_name=_("last hardware capture"),
        null=True,
        blank=True,
    )

    tags = models.ManyToManyField(
        Attribute,
        blank=True,
        verbose_name=_("tags"),
        related_name='tags'
    )

    sync_start_date = models.DateTimeField(
        verbose_name=_('sync start date'),
        null=True,
    )

    sync_end_date = models.DateTimeField(
        verbose_name=_("sync end date"),
        null=True,
    )

    sync_user = models.ForeignKey(
        User,
        verbose_name=_("sync user"),
        null=True,
    )

    sync_attributes = models.ManyToManyField(
        Attribute,
        blank=True,
        verbose_name=_("sync attributes"),
        help_text=_("attributes sent")
    )

    product = models.CharField(
        verbose_name=_("product"),
        max_length=80,
        null=True,
        blank=True,
        unique=False
    )

    machine = models.CharField(
        verbose_name=_("machine"),
        max_length=1,
        null=False,
        choices=MACHINE_CHOICES,
        default='P'
    )

    cpu = models.CharField(
        verbose_name=_("CPU"),
        max_length=50,
        null=True,
        blank=True,
        unique=False
    )

    ram = models.BigIntegerField(
        verbose_name=_("RAM"),
        null=True,
        blank=True
    )

    storage = models.BigIntegerField(
        verbose_name=_("storage"),
        null=True,
        blank=True
    )

    disks = models.SmallIntegerField(
        verbose_name=_("disks"),
        null=True,
        blank=True
    )

    mac_address = models.CharField(
        verbose_name=_("MAC address"),
        max_length=60,  # size for 5
        null=True,
        blank=True,
        unique=False
    )

    objects = ComputerManager()
    productive = ProductiveManager()
    unproductive = UnproductiveManager()
    subscribed = SubscribedManager()
    unsubscribed = UnsubscribedManager()
    active = ActiveManager()
    inactive = InactiveManager()

    def __init__(self, *args, **kwargs):
        super(Computer, self).__init__(*args, **kwargs)

        if not settings.MIGASFREE_REMOTE_ADMIN_LINK:
            self._actions = None
            return

        self._actions = []
        template = Template(settings.MIGASFREE_REMOTE_ADMIN_LINK)
        context = {'computer': self}
        for node in template.nodelist:
            try:
                token = node.filter_expression.token
                if not token.startswith('computer'):
                    context[token] = ','.join(list(
                        self.sync_attributes.filter(
                            property_att__prefix=token
                        ).values_list('value', flat=True)
                    ))
            except:
                pass

        remote_admin = template.render(Context(context))

        for element in remote_admin.split(' '):
            protocol = element.split('://')[0]
            self._actions.append([protocol, element])

    def get_all_attributes(self):
        return list(self.tags.values_list('id', flat=True)) \
            + list(self.sync_attributes.values_list('id', flat=True))

    def login(self):
        return u'{} ({})'.format(
            self.sync_user.name,
            self.sync_user.fullname.strip()
        )

    def change_status(self, status):
        if status not in list(dict(self.STATUS_CHOICES).keys()):
            return False

        self.status = status
        self.save()

        return True

    def update_sync_user(self, user):
        self.sync_user = user
        self.sync_start_date = datetime.now()
        self.save()

    def update_identification(self, name, version, uuid, ip_address):
        self.name = name
        self.version = version
        self.uuid = uuid
        self.ip_address = ip_address
        self.save()

    def update_software_history(self, history):
        if history:
            if self.software_history:
                self.software_history += '\n\n' + history
            else:
                self.software_history = history
            self.save()

    def update_software_inventory(self, pkgs):
        if pkgs:
            self.software_inventory = pkgs
            self.save()

    def update_last_hardware_capture(self):
        self.last_hardware_capture = datetime.now()
        self.save()

    def update_hardware_resume(self):
        from . import HwNode as Node

        try:
            self.product = Node.objects.get(
                computer=self.id, parent=None
            ).get_product()
        except ObjectDoesNotExist:
            self.product = None

        self.machine = 'V' if Node.get_is_vm(self.id) else 'P'
        self.cpu = Node.get_cpu(self.id)
        self.ram = Node.get_ram(self.id)
        self.disks, self.storage = Node.get_storage(self.id)
        self.mac_address = Node.get_mac_address(self.id)

        self.save()

    def logical_devices(self, attributes=None):
        if not attributes:
            attributes = self.sync_attributes.values_list('id', flat=True)

        return DeviceLogical.objects.filter(
            attributes__in=attributes
        ).distinct()

    logical_devices.allow_tags = True
    logical_devices.short_description = _('Logical Devices')

    @staticmethod
    def replacement(source, target):
        swap_m2m(source.tags, target.tags)
        source.default_logical_device, target.default_logical_device = (
            target.default_logical_device, source.default_logical_device
        )

        # SWAP CID
        source_cid = source.get_cid_attribute()
        target_cid = target.get_cid_attribute()
        swap_m2m(source_cid.devicelogical_set, target_cid.devicelogical_set)
        swap_m2m(source_cid.faultdef_set, target_cid.faultdef_set)
        swap_m2m(source_cid.repository_set, target_cid.repository_set)
        swap_m2m(source_cid.ExcludeAttribute, target_cid.ExcludeAttribute)
        swap_m2m(source_cid.attributeset_set, target_cid.attributeset_set)
        swap_m2m(
            source_cid.ExcludeAttributeGroup, target_cid.ExcludeAttributeGroup
        )
        swap_m2m(source_cid.scheduledelay_set, target_cid.scheduledelay_set)

        source.status, target.status = target.status, source.status

        # finally save changes!!! (order is important)
        source.save()
        target.save()

    def get_cid_attribute(self):
        prop = Property.objects.get(prefix='CID', active=True)
        cid_att, _ = Attribute.objects.get_or_create(
            property_att=prop,
            value=str(self.id),
            defaults={'description': self.get_cid_description()}
        )

        return cid_att

    def get_cid_description(self):
        desc = list(settings.MIGASFREE_COMPUTER_SEARCH_FIELDS)
        if 'id' in desc:
            desc.remove('id')

        return str(self.__getattribute__(desc[0]))

    def get_replacement_info(self):
        cid = self.get_cid_attribute()

        return remove_empty_elements_from_dict({
            ugettext("Computer"): self.__str__(),
            ugettext("Status"): ugettext(self.status),
            ugettext("Tags"): ', '.join(str(x) for x in self.tags.all()),
            ugettext("Faults"): ', '.join(
                str(x) for x in cid.faultdef_set.all()
            ),
            ugettext("Repositories"): ', '.join(
                str(x) for x in cid.repository_set.all()
            ),
            ugettext("Repositories (excluded)"): ', '.join(
                str(x) for x in cid.ExcludeAttribute.all()
            ),
            ugettext("Sets"): ', '.join(
                str(x) for x in cid.attributeset_set.all()
            ),
            ugettext("Sets (excluded)"): ', '.join(
                str(x) for x in cid.ExcludeAttributeGroup.all()
            ),
            ugettext("Delays"): ', '.join(
                str(x) for x in cid.scheduledelay_set.all()
            ),
            ugettext("Logical devices"): ', '.join(
                str(x) for x in self.logical_devices()
            ),
            ugettext("Default logical device"): self.default_logical_device.__str__(),
        })

    def append_devices(self, computer_id):
        try:
            target = Computer.objects.get(pk=computer_id)
            target.devices_logical.add(*self.devices_logical.all())
        except ObjectDoesNotExist:
            pass

    def __str__(self):
        if settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0] == 'id':
            return u'CID-{}'.format(self.id)
        else:
            return u'{} (CID-{})'.format(self.get_cid_description(), self.id)

    class Meta:
        app_label = 'server'
        verbose_name = _("Computer")
        verbose_name_plural = _("Computers")
        permissions = (("can_save_computer", "Can save Computer"),)


from .status_log import StatusLog


@receiver(pre_save, sender=Computer)
def pre_save_computer(sender, instance, **kwargs):
    if instance.id:
        old_obj = Computer.objects.get(pk=instance.id)
        if old_obj.status != instance.status:
            StatusLog.objects.create(instance)


@receiver(post_save, sender=Computer)
def post_save_computer(sender, instance, created, **kwargs):
    if created:
        StatusLog.objects.create(instance)

    if instance.status in ['available', 'unsubscribed']:
        instance.tags.clear()

        cid = instance.get_cid_attribute()
        cid.devicelogical_set.clear()
        cid.faultdef_set.clear()
        cid.repository_set.clear()
        cid.ExcludeAttribute.clear()
        cid.attributeset_set.clear()
        cid.ExcludeAttributeGroup.clear()
        cid.scheduledelay_set.clear()
