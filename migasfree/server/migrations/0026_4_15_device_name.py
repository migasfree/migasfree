# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0025_4_15_hardware'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='name'),
        ),
    ]
