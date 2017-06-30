# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import migasfree.server.models.common


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0022_4_14_computers'),
        ('catalog', '0002_4_14_versions'),
    ]

    operations = [
        migrations.CreateModel(
            name='PackagesByProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('packages_to_install', models.TextField(blank=True, verbose_name='packages to install')),
            ],
            options={
                'verbose_name': 'Packages by Project',
                'verbose_name_plural': 'Packages by Projects',
                'permissions': (('can_save_packagesbyproject', 'Can save packages by project'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.AlterField(
            model_name='application',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='name'),
        ),
        migrations.AlterUniqueTogether(
            name='application',
            unique_together=set([]),
        ),
        migrations.AddField(
            model_name='packagesbyproject',
            name='application',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='catalog.Application', verbose_name='application',
                related_name='packages_by_project'
            ),
        ),
        migrations.AddField(
            model_name='packagesbyproject',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project', verbose_name='project'
            ),
        ),
        migrations.RemoveField(
            model_name='application',
            name='packages_to_install',
        ),
        migrations.RemoveField(
            model_name='application',
            name='project',
        ),
        migrations.AlterUniqueTogether(
            name='packagesbyproject',
            unique_together={('application', 'project')},
        ),
    ]
