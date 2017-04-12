# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0018_4_14_properties'),
    ]

    operations = [
        migrations.RenameModel(old_name='Version', new_name='Project'),
        migrations.RemoveField(model_name='Project', name='computerbase'),
        migrations.RemoveField(model_name='Project', name='base'),
        migrations.RenameField(
            model_name='Project',
            old_name='autoregister',
            new_name='auto_register_computers'
        ),
        migrations.AlterField(
            model_name='Project',
            name='auto_register_computers',
            field=models.BooleanField(
                default=False,
                help_text='Is not needed a user for register computers in database and get the keys.',
                verbose_name='auto register computers'
            ),
        ),
        migrations.AlterModelOptions(
            name='Project',
            options={
                'ordering': ['name'],
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
                'permissions': (('can_save_project', 'Can save Project'),),
            },
        ),
        migrations.RenameField(
            model_name='Deployment',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Deployment',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.AlterModelOptions(
            name='deployment',
            options={
                'ordering': ['project__name', 'name'],
                'permissions': (('can_save_deployment', 'Can save Deployment'),),
                'verbose_name': 'Deployment',
                'verbose_name_plural': 'Deployments'
            },
        ),
        migrations.AlterUniqueTogether(
            name='deployment',
            unique_together={('name', 'project')},
        ),
        migrations.RenameField(
            model_name='Store',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Store',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.AlterModelOptions(
            name='Store',
            options={
                'ordering': ['name', 'project'],
                'permissions': (('can_save_store', 'Can save Store'),),
                'verbose_name': 'Store',
                'verbose_name_plural': 'Stores'
            },
        ),
        migrations.RenameField(
            model_name='Computer',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Computer',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.RenameField(
            model_name='Error',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Error',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.RenameField(
            model_name='Fault',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Fault',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.RenameField(
            model_name='Migration',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Migration',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.RenameField(
            model_name='Synchronization',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Synchronization',
            name='project',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.RenameField(
            model_name='UserProfile',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='UserProfile',
            name='project',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.AlterField(
            model_name='query',
            name='code',
            field=models.TextField(
                blank=True,
                default=b"query = Package.objects.filter(project=PROJECT).filter(deployment__id__exact=None)\nfields = ('id', 'name', 'store__name')\ntitles = ('id', 'name', 'store')",
                help_text='Django Code: project = user.project, query = QuerySet, fields = list of QuerySet fields names to show, titles = list of QuerySet fields titles',
                null=True,
                verbose_name='code'
            ),
        ),
        migrations.RenameField(
            model_name='DeviceDriver',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='DeviceDriver',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.AlterUniqueTogether(
            name='DeviceDriver',
            unique_together={('model', 'project', 'feature')},
        ),
        migrations.RenameField(
            model_name='Package',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Package',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.AlterUniqueTogether(
            name='package',
            unique_together={('name', 'project')},
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_property SET name=%s, prefix=%s WHERE id=4;",
                [
                    "PROJECT",
                    "PRJ"
                ]
            )],
            [(
                "UPDATE server_property SET name=%s, prefix=%s WHERE id=4;",
                [
                    "VERSION",
                    "VER"
                ]
            )]
        ),
    ]
