# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models


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
    ]
