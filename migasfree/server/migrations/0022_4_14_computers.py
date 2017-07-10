# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0021_4_14_hardware'),
    ]

    operations = [
        migrations.AddField(
            model_name='computer',
            name='forwarded_ip_address',
            field=models.CharField(
                blank=True, max_length=50,
                null=True, verbose_name='forwarded ip address'
            ),
        ),
        migrations.AddField(
            model_name='computer',
            name='fqdn',
            field=models.CharField(
                blank=True, max_length=255,
                null=True, verbose_name='full qualified domain name'
            ),
        ),
        migrations.AddField(
            model_name='computer',
            name='comment',
            field=models.TextField(
                blank=True, null=True,
                verbose_name='comment'
            ),
        ),
        migrations.AlterField(
            model_name='computer',
            name='software_inventory',
            field=models.TextField(
                verbose_name="software inventory",
                null=True,
                blank=True,
            ),
        ),
    ]
