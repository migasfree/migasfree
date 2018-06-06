# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.db import models
from django.db.models.signals import pre_save, post_save, pre_delete
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import format_html
from django.utils.translation import ugettext, ugettext_lazy as _
from django.template import Context, Template
from django.conf import settings

from ..utils import (
    swap_m2m, remove_empty_elements_from_dict,
    strfdelta, list_difference, html_label,
)

from . import (
    Project, DeviceLogical, User,
    Attribute, ServerAttribute, BasicProperty,
    MigasLink, Property
)


class DomainComputerManager(models.Manager):
    def scope(self, user):
        qs = super(DomainComputerManager, self).get_queryset()
        if not user.is_view_all():
            qs = qs.filter(id__in=user.get_computers())
        return qs.defer("software_inventory", "software_history")


class ProductiveManager(DomainComputerManager):
    def get_queryset(self):
        return super(ProductiveManager, self).get_queryset().filter(
            status__in=Computer.PRODUCTIVE_STATUS
        )

    def scope(self, user):
        return super(ProductiveManager, self).scope(user).filter(
            status__in=Computer.PRODUCTIVE_STATUS
        )


class UnproductiveManager(DomainComputerManager):
    def get_queryset(self):
        return super(UnproductiveManager, self).get_queryset().exclude(
            status__in=Computer.PRODUCTIVE_STATUS
        )

    def scope(self, user):
        return super(UnproductiveManager, self).scope(user).exclude(
            status__in=Computer.PRODUCTIVE_STATUS
        )


class SubscribedManager(DomainComputerManager):
    def get_queryset(self):
        return super(SubscribedManager, self).get_queryset().exclude(
            status='unsubscribed'
        )

    def scope(self, user):
        return super(SubscribedManager, self).scope(user).exclude(
            status='unsubscribed'
        )


class UnsubscribedManager(DomainComputerManager):
    def get_queryset(self):
        return super(UnsubscribedManager, self).get_queryset().filter(
            status='unsubscribed'
        )

    def scope(self, user):
        return super(UnsubscribedManager, self).scope(user).filter(
            status='unsubscribed'
        )


class ActiveManager(DomainComputerManager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(
            status__in=Computer.ACTIVE_STATUS
        )

    def scope(self, user):
        return super(ActiveManager, self).scope(user).filter(
            status__in=Computer.ACTIVE_STATUS
        )


class InactiveManager(DomainComputerManager):
    def get_queryset(self):
        return super(InactiveManager, self).get_queryset().exclude(
            status__in=Computer.ACTIVE_STATUS
        )

    def scope(self, user):
        return super(InactiveManager, self).scope(user).exclude(
            status__in=Computer.ACTIVE_STATUS
        )


class ComputerManager(DomainComputerManager):
    def create(self, name, project, uuid, ip=None):
        obj = Computer()
        obj.name = name
        obj.project = project
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
    UNSUBSCRIBED_STATUS = ['unsubscribed']

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

    fqdn = models.CharField(
        verbose_name=_('full qualified domain name'),
        max_length=255,
        null=True,
        blank=True,
        unique=False
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name=_("project")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('entry date'),
        help_text=_('Date of entry into the migasfree system')
    )
    updated_at = models.DateTimeField(auto_now=True)

    ip_address = models.CharField(
        verbose_name=_("ip address"),
        max_length=50,
        null=True,
        blank=True
    )

    forwarded_ip_address = models.CharField(
        verbose_name=_("forwarded ip address"),
        max_length=50,
        null=True,
        blank=True
    )

    software_inventory = models.TextField(
        verbose_name=_("software inventory"),
        null=True,
        blank=True,
    )

    software_history = models.TextField(
        verbose_name=_("software history"),
        default="",
        null=True,
        blank=True
    )

    default_logical_device = models.ForeignKey(
        DeviceLogical,
        on_delete=models.CASCADE,
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
        ServerAttribute,
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
        on_delete=models.CASCADE,
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

    comment = models.TextField(
        verbose_name=_("comment"),
        null=True,
        blank=True
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
        template = Template(' '.join(settings.MIGASFREE_REMOTE_ADMIN_LINK))
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

    def update_identification(self, name, fqdn, project, uuid, ip_address, forwarded_ip_address):
        self.name = name
        self.fqdn = fqdn
        self.project = project
        self.uuid = uuid
        self.ip_address = ip_address
        self.forwarded_ip_address = forwarded_ip_address
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

    def update_logical_devices(self, devices):
        """
        :param devices: [id1, id2, id3, ...]
        :return: void
        """
        cid_attribute = self.get_cid_attribute()
        initial_logical_devices = list(
            self.assigned_logical_devices_to_cid().values_list('id', flat=True)
        )

        for pk in list_difference(devices, initial_logical_devices):
            DeviceLogical.objects.get(pk=pk).attributes.add(cid_attribute)

        for pk in list_difference(initial_logical_devices, devices):
            DeviceLogical.objects.get(pk=pk).attributes.remove(cid_attribute)

    def logical_devices(self, attributes=None):
        if not attributes:
            attributes = self.sync_attributes.values_list('id', flat=True)

        return DeviceLogical.objects.filter(
            attributes__in=attributes
        ).distinct()

    logical_devices.short_description = _('Logical Devices')

    def inflected_logical_devices(self):
        return self.logical_devices().exclude(
            attributes__in=[self.get_cid_attribute().pk]
        )

    inflected_logical_devices.short_description = _('Inflected Logical Devices')

    def assigned_logical_devices_to_cid(self):
        return self.logical_devices().difference(self.inflected_logical_devices())

    assigned_logical_devices_to_cid.short_description = _('Assigned Logical Devices to CID')

    def get_architecture(self):
        from .hw_node import HwNode

        query = HwNode.objects.filter(
            computer=self.id,
            class_name='processor',
            width__gt=0
        )
        if query.count():
            return query[0].width

        query = HwNode.objects.filter(
            computer=self.id,
            class_name='system',
            width__gt=0
        )
        if query.count():
            return query[0].width

        return None

    def is_docker(self):
        from .hw_node import HwNode

        return HwNode.get_is_docker(self.id)

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
        swap_m2m(source_cid.faultdefinition_set, target_cid.faultdefinition_set)
        swap_m2m(source_cid.deployment_set, target_cid.deployment_set)
        swap_m2m(source_cid.ExcludeAttribute, target_cid.ExcludeAttribute)
        swap_m2m(source_cid.attributeset_set, target_cid.attributeset_set)
        swap_m2m(
            source_cid.ExcludedAttributesGroup,
            target_cid.ExcludedAttributesGroup
        )
        swap_m2m(source_cid.scheduledelay_set, target_cid.scheduledelay_set)
        swap_m2m(
            source_cid.PolicyIncludedAttributes,
            target_cid.PolicyIncludedAttributes
        )
        swap_m2m(
            source_cid.PolicyExcludedAttributes,
            target_cid.PolicyExcludedAttributes
        )
        swap_m2m(
            source_cid.PolicyGroupIncludedAttributes,
            target_cid.PolicyGroupIncludedAttributes
        )
        swap_m2m(
            source_cid.PolicyGroupExcludedAttributes,
            target_cid.PolicyGroupExcludedAttributes
        )
        swap_m2m(
            source_cid.ScopeIncludedAttribute,
            target_cid.ScopeIncludedAttribute
        )
        swap_m2m(
            source_cid.ScopeExcludedAttribute,
            target_cid.ScopeExcludedAttribute
        )
        swap_m2m(
            source_cid.DomainIncludedAttribute,
            target_cid.DomainIncludedAttribute
        )
        swap_m2m(
            source_cid.DomainExcludedAttribute,
            target_cid.DomainExcludedAttribute
        )

        source.status, target.status = target.status, source.status

        # finally save changes!!! (order is important)
        source.save()
        target.save()

    def get_cid_attribute(self):
        cid_att, _ = Attribute.objects.get_or_create(
            property_att=BasicProperty.objects.get(prefix='CID'),
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
                str(x) for x in cid.faultdefinition_set.all()
            ),
            ugettext("Deployments"): ', '.join(
                str(x) for x in cid.deployment_set.all()
            ),
            ugettext("Deployments (excluded)"): ', '.join(
                str(x) for x in cid.ExcludeAttribute.all()
            ),
            ugettext("Sets"): ', '.join(
                str(x) for x in cid.attributeset_set.all()
            ),
            ugettext("Sets (excluded)"): ', '.join(
                str(x) for x in cid.ExcludedAttributesGroup.all()
            ),
            ugettext("Delays"): ', '.join(
                str(x) for x in cid.scheduledelay_set.all()
            ),
            ugettext("Logical devices"): ', '.join(
                str(x) for x in self.logical_devices()
            ),
            ugettext("Default logical device"): self.default_logical_device.__str__(),
            ugettext("Policies (included)"): ', '.join(
                str(x) for x in cid.PolicyIncludedAttributes.all()
            ),
            ugettext("Policies (excluded)"): ', '.join(
                str(x) for x in cid.PolicyExcludedAttributes.all()
            ),
            ugettext("Policy Groups (included)"): ', '.join(
                str(x) for x in cid.PolicyGroupIncludedAttributes.all()
            ),
            ugettext("Policy Groups (excluded)"): ', '.join(
                str(x) for x in cid.PolicyGroupExcludedAttributes.all()
            ),
        })

    def append_devices(self, computer_id):
        try:
            target = Computer.objects.get(pk=computer_id)
            target.devices_logical.add(*self.devices_logical.all())
        except ObjectDoesNotExist:
            pass

    def unchecked_errors(self):
        from .error import Error
        count = Error.unchecked.filter(computer__pk=self.pk).count()

        return html_label(
            count=count,
            title=_('Unchecked Errors'),
            link='{}?computer__id__exact={}&checked__exact={}'.format(
                reverse('admin:server_error_changelist'),
                self.pk,
                0,
            ),
            level='danger'
        )

    unchecked_errors.short_description = _('Unchecked Errors')

    def errors(self):
        from .error import Error
        count = Error.objects.filter(computer__pk=self.pk).count()

        return html_label(
            count=count,
            title=_('Errors'),
            link='{}?computer__id__exact={}'.format(
                reverse('admin:server_error_changelist'),
                self.pk,
            )
        )

    errors.short_description = _('Errors')

    def unchecked_faults(self):
        from .fault import Fault
        count = Fault.unchecked.filter(computer__pk=self.pk).count()

        return html_label(
            count=count,
            title=_('Unchecked Faults'),
            link='{}?computer__id__exact={}&checked__exact={}'.format(
                reverse('admin:server_fault_changelist'),
                self.pk,
                0,
            ),
            level='danger'
        )

    unchecked_faults.short_description = _('Unchecked Faults')

    def faults(self):
        from .fault import Fault
        count = Fault.objects.filter(computer__pk=self.pk).count()

        return html_label(
            count=count,
            title=_('Faults'),
            link='{}?computer__id__exact={}'.format(
                reverse('admin:server_fault_changelist'),
                self.pk,
            )
        )

    faults.short_description = _('Faults')

    def last_sync_time(self):
        if not self.sync_start_date:
            return ''

        now = datetime.now()
        delayed_time = now - timedelta(
            seconds=settings.MIGASFREE_SECONDS_MESSAGE_ALERT
        )
        is_updating = not self.sync_end_date or self.sync_end_date < self.sync_start_date

        if is_updating:
            diff = now - self.sync_start_date
        else:
            diff = self.sync_end_date - self.sync_start_date

        if self.sync_start_date < delayed_time and is_updating:
            return format_html(
                u'<span class="label label-warning" title="{}">'
                u'<i class="fas fa-exclamation-triangle"></i> {}</span>'.format(
                    _('Delayed Computer'),
                    strfdelta(diff, _('{days} days, {hours:02d}:{minutes:02d}:{seconds:02d}'))
                )
            )

        if is_updating:
            return format_html(
                u'<span class="label label-info">'
                u'<i class="fas fa-sync-alt"></i> {}</span>'.format(
                    _('Updating...'),
                )
            )

        return strfdelta(diff, '{hours:02d}:{minutes:02d}:{seconds:02d}')

    last_sync_time.short_description = _('Last Update Time')

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
        cid.faultdefinition_set.clear()
        cid.deployment_set.clear()
        cid.ExcludeAttribute.clear()
        cid.attributeset_set.clear()
        cid.ExcludedAttributesGroup.clear()
        cid.scheduledelay_set.clear()


@receiver(pre_delete, sender=Computer)
def pre_delete_computer(sender, instance, **kwargs):
    Attribute.objects.filter(
        property_att=Property.objects.get(prefix='CID'),
        value=instance.id
    ).delete()
