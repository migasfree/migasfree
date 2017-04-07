# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0003_4_10_changes'),
    ]

    operations = [
        migrations.AddField(
            model_name='computer',
            name='cpu',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='CPU'),
        ),
        migrations.AddField(
            model_name='computer',
            name='disks',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='disks'),
        ),
        migrations.AddField(
            model_name='computer',
            name='mac_address',
            field=models.CharField(blank=True, max_length=60, null=True, verbose_name='MAC address'),
        ),
        migrations.AddField(
            model_name='computer',
            name='machine',
            field=models.CharField(
                choices=[(b'P', 'Physical'), (b'V', 'Virtual')],
                default=b'P',
                max_length=1,
                verbose_name='machine'
            ),
        ),
        migrations.AddField(
            model_name='computer',
            name='product',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='product'),
        ),
        migrations.AddField(
            model_name='computer',
            name='ram',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='RAM'),
        ),
        migrations.AddField(
            model_name='computer',
            name='storage',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='storage'),
        ),
    ]
