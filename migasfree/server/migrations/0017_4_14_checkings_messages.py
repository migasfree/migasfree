# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0016_4_14_repositories'),
    ]

    operations = [
        migrations.RenameField(
            model_name='Message',
            old_name='date',
            new_name='updated_at',
        ),
        migrations.AlterField(
            model_name='Message',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                default=django.utils.timezone.now,
                verbose_name='date'
            ),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='MessageServer',
        ),
        migrations.DeleteModel(
            name='Checking',
        ),
    ]
