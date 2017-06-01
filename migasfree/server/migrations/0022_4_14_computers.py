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
    ]
