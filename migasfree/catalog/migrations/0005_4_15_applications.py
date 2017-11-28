# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0024_4_15_devices'),
        ('catalog', '0004_4_14_policies'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='available_for_attributes',
            field=models.ManyToManyField(
                blank=True, to='server.Attribute',
                verbose_name='available for attributes'
            ),
        ),
    ]
