# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0019_4_14_versions'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deviceconnection',
            old_name='devicetype',
            new_name='device_type',
        ),
        migrations.RenameField(
            model_name='devicedriver',
            old_name='install',
            new_name='packages_to_install',
        ),
        migrations.RenameField(
            model_name='devicemodel',
            old_name='devicetype',
            new_name='device_type',
        ),
        migrations.RenameField(
            model_name='devicelogical',
            old_name='name',
            new_name='alternative_feature_name',
        ),
        migrations.AlterField(
            model_name='devicelogical',
            name='alternative_feature_name',
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                verbose_name='alternative feature name'
            ),
        ),
        migrations.AlterUniqueTogether(
            name='deviceconnection',
            unique_together={('device_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='devicemodel',
            unique_together={('device_type', 'manufacturer', 'name')},
        ),
    ]
