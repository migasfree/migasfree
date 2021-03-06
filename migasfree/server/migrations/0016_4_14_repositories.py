# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-04-05 11:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0015_4_14_schedules'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Repository',
            new_name='Deployment'
        ),
        migrations.RenameField(
            model_name='Deployment',
            old_name='active',
            new_name='enabled',
        ),
        migrations.AlterField(
            model_name='Deployment',
            name='enabled',
            field=models.BooleanField(
                default=True,
                help_text='if you uncheck this field, deployment is disabled for all computers.',
                verbose_name='enabled'
            ),
        ),
        migrations.RenameField(
            model_name='Deployment',
            old_name='date',
            new_name='start_date',
        ),
        migrations.AlterField(
            model_name='Deployment',
            name='start_date',
            field=models.DateField(
                default=django.utils.timezone.now,
                verbose_name='start date'
            ),
        ),
        migrations.RenameField(
            model_name='Deployment',
            old_name='packages',
            new_name='available_packages',
        ),
        migrations.AlterField(
            model_name='Deployment',
            name='available_packages',
            field=models.ManyToManyField(
                blank=True,
                help_text='If a computer has installed one of these packages it will be updated',
                to='server.Package',
                verbose_name='available packages'
            ),
        ),
        migrations.RenameField(
            model_name='Deployment',
            old_name='attributes',
            new_name='included_attributes',
        ),
        migrations.AlterField(
            model_name='Deployment',
            name='included_attributes',
            field=models.ManyToManyField(
                blank=True,
                to='server.Attribute',
                verbose_name='included attributes'
            ),
        ),
        migrations.RenameField(
            model_name='Deployment',
            old_name='excludes',
            new_name='excluded_attributes',
        ),
        migrations.AlterField(
            model_name='Deployment',
            name='excluded_attributes',
            field=models.ManyToManyField(
                blank=True,
                related_name='ExcludeAttribute',
                to='server.Attribute',
                verbose_name='excluded attributes'
            ),
        ),
        migrations.RenameField(
            model_name='Deployment',
            old_name='toinstall',
            new_name='packages_to_install',
        ),
        migrations.AlterField(
            model_name='Deployment',
            name='packages_to_install',
            field=models.TextField(
                blank=True,
                help_text='Mandatory packages to install each time',
                null=True,
                verbose_name='packages to install'
            ),
        ),
        migrations.RenameField(
            model_name='Deployment',
            old_name='toremove',
            new_name='packages_to_remove',
        ),
        migrations.AlterField(
            model_name='Deployment',
            name='packages_to_remove',
            field=models.TextField(
                blank=True,
                help_text='Mandatory packages to remove each time',
                null=True,
                verbose_name='packages to remove'
            ),
        ),
        migrations.RenameField(
            model_name='Deployment',
            old_name='defaultpreinclude',
            new_name='default_preincluded_packages',
        ),
        migrations.AlterField(
            model_name='Deployment',
            name='default_preincluded_packages',
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name='default pre-included packages'
            ),
        ),
        migrations.RenameField(
            model_name='Deployment',
            old_name='defaultinclude',
            new_name='default_included_packages',
        ),
        migrations.AlterField(
            model_name='Deployment',
            name='default_included_packages',
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name='default included packages'
            ),
        ),
        migrations.RenameField(
            model_name='Deployment',
            old_name='defaultexclude',
            new_name='default_excluded_packages',
        ),
        migrations.AlterField(
            model_name='Deployment',
            name='default_excluded_packages',
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name='default excluded packages'
            ),
        ),
        migrations.AlterModelOptions(
            name='Deployment',
            options={
                'ordering': ['version__name', 'name'],
                'permissions': (('can_save_deployment', 'Can save Deployment'),),
                'verbose_name': 'Deployment',
                'verbose_name_plural': 'Deployments'
            },
        ),
        migrations.AlterField(
            model_name='query',
            name='code',
            field=models.TextField(blank=True, default=b"query = Package.objects.filter(version=VERSION).filter(deployment__id__exact=None)\nfields = ('id', 'name', 'store__name')\ntitles = ('id', 'name', 'store')", help_text='Django Code: version = user.version, query = QuerySet, fields = list of QuerySet fields names to show, titles = list of QuerySet fields titles', null=True, verbose_name='code'),
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_checking SET code=%s, description=%s WHERE id=3;",
                [
                    "from migasfree.server.models import Package\nresult = Package.objects.filter(deployment__id__exact=None).count()\nurl = '/admin/server/package/?deployment__isnull=True'\nalert = 'warning'\nmsg = 'Package/Set orphan'\ntarget = 'server'\n",
                    "Packages that have not been assigned to any deployment"
                ]
            )],
            [(
                "UPDATE server_checking SET code=%s, description=%s WHERE id=3;",
                [
                    "from migasfree.server.models import Package\nresult = Package.objects.filter(repository__id__exact=None).count()\nurl = '/admin/server/package/?repository__isnull=True'\nalert = 'warning'\nmsg = 'Package/Set orphan'\ntarget = 'server'\n",
                    "Packages that have not been assigned to any repository"
                ]
            )]
        ),
    ]
