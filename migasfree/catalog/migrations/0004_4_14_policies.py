# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import migasfree.server.models.common


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_4_14_packages_by_project'),
    ]

    operations = [
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('enabled', models.BooleanField(
                    default=True,
                    help_text='if you uncheck this field, the policy is disabled for all computers.',
                    verbose_name='enabled'
                )),
                ('exclusive', models.BooleanField(
                    default=True,
                    verbose_name='exclusive'
                )),
                ('comment', models.TextField(blank=True, null=True, verbose_name='comment')),
                ('excluded_attributes', models.ManyToManyField(
                    blank=True, related_name='PolicyExcludedAttributes',
                    to='server.Attribute', verbose_name='excluded attributes'
                )),
                ('included_attributes', models.ManyToManyField(
                    blank=True, related_name='PolicyIncludedAttributes',
                    to='server.Attribute', verbose_name='included attributes'
                )),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Policy',
                'verbose_name_plural': 'Policies',
                'permissions': (('can_save_policy', 'Can save Policy'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='PolicyGroup',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('priority', models.IntegerField(verbose_name='priority')),
                ('applications', models.ManyToManyField(
                    blank=True, to='catalog.Application', verbose_name='application'
                )),
                ('excluded_attributes', models.ManyToManyField(
                    blank=True, related_name='PolicyGroupExcludedAttributes',
                    to='server.Attribute', verbose_name='excluded attributes'
                )),
                ('included_attributes', models.ManyToManyField(
                    blank=True, related_name='PolicyGroupIncludedAttributes',
                    to='server.Attribute', verbose_name='included attributes'
                )),
                ('policy', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='catalog.Policy', verbose_name='policy'
                )),
            ],
            options={
                'ordering': ['policy__name', 'priority'],
                'verbose_name': 'Policy Group',
                'verbose_name_plural': 'Policy Groups',
                'permissions': (('can_save_policygroup', 'Can save Policy Group'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.AlterUniqueTogether(
            name='policygroup',
            unique_together={('policy', 'priority')},
        ),
        migrations.AlterUniqueTogether(
            name='policy',
            unique_together={('name',)},
        ),
    ]
