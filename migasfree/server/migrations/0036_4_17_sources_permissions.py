# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0035_4_17_scopes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='externalsource',
            options={
                'permissions': (('can_save_externalsource', 'Can save External Source'),),
                'verbose_name': 'Deployment (external source)',
                'verbose_name_plural': 'Deployments (external source)'
            },
        ),
        migrations.AlterModelOptions(
            name='internalsource',
            options={
                'permissions': (('can_save_internalsource', 'Can save Internal Source'),),
                'verbose_name': 'Deployment (internal source)',
                'verbose_name_plural': 'Deployments (internal source)'
            },
        ),
    ]
