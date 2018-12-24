# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0029_4_16_domains_fixtures'),
    ]

    operations = [
        migrations.AlterField(
            model_name='computer',
            name='default_logical_device',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='server.DeviceLogical', verbose_name='default logical device'
            ),
        ),
    ]
