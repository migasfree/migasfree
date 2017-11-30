# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0024_4_15_devices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hwnode',
            name='clock',
            field=models.BigIntegerField(null=True, verbose_name='clock'),
        ),
    ]
