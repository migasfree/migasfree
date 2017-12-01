# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import migasfree.catalog.models

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
        migrations.AlterField(
            model_name='application',
            name='icon',
            field=models.ImageField(
                null=True, storage=migasfree.catalog.models.MediaFileSystemStorage(),
                upload_to=migasfree.catalog.models.upload_path_handler, verbose_name='icon'
            ),
        ),
    ]
