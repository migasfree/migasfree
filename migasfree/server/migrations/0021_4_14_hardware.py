# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models
from django.core.exceptions import ObjectDoesNotExist

from migasfree.server.models import HwNode as Node


def insert_initial_hardware_resume(apps, schema_editor):
    Computer = apps.get_model('server', 'Computer')
    db_alias = schema_editor.connection.alias

    for computer in Computer.objects.using(db_alias).all():
        if not computer.cpu:
            try:
                computer.product = Node.objects.using(db_alias).get(
                    computer=computer.id, parent=None
                ).get_product()
            except ObjectDoesNotExist:
                computer.product = None

            computer.machine = 'V' if Node.get_is_vm(computer.id) else 'P'
            computer.cpu = Node.get_cpu(computer.id)
            computer.ram = Node.get_ram(computer.id)
            computer.disks, computer.storage = Node.get_storage(computer.id)
            computer.mac_address = Node.get_mac_address(computer.id)

            computer.save()


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0020_4_14_devices'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='hwconfiguration',
            options={
                'verbose_name': 'Hardware Configuration',
                'verbose_name_plural': 'Hardware Configurations'
            },
        ),
        migrations.RenameField(
            model_name='hwnode',
            old_name='classname',
            new_name='class_name',
        ),
        migrations.RenameField(
            model_name='hwnode',
            old_name='businfo',
            new_name='bus_info',
        ),
        migrations.AlterField(
            model_name='hwnode',
            name='bus_info',
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name='bus info'
            ),
        ),
        migrations.RemoveField(
            model_name='hwnode',
            name='icon',
        ),
        migrations.RunPython(
            insert_initial_hardware_resume,
            migrations.RunPython.noop
        ),
    ]
