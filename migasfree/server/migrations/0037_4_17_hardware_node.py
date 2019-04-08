# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0036_4_17_sources_permissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hwnode',
            name='width',
            field=models.BigIntegerField(null=True, verbose_name='width'),
        ),
    ]
