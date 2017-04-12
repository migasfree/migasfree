# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
        ('server', '0019_4_14_versions'),
    ]

    operations = [
        migrations.DeleteModel(name='Application'),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('description', markdownx.models.MarkdownxField(
                    blank=True,
                    verbose_name='description',
                    help_text='markdown syntax allowed'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('packages_to_install', models.TextField(verbose_name='packages to install', blank=True)),
                ('score', models.IntegerField(
                    choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)],
                    default=1,
                    verbose_name='score',
                    help_text='Relevance to the organization'
                )),
                ('icon', models.ImageField(verbose_name='icon', upload_to=b'catalog_icons/', null=True)),
                ('level', models.CharField(
                    choices=[(b'U', 'User'), (b'A', 'Admin')],
                    default=b'U',
                    max_length=1,
                    verbose_name='level'
                )),
                ('category', models.IntegerField(
                    choices=[
                        (1, 'Accessories'), (2, 'Books'), (3, 'Developers Tools'),
                        (4, 'Education'), (5, 'Fonts'), (6, 'Games'),
                        (7, 'Graphics'), (8, 'Internet'), (9, 'Medicine'),
                        (10, 'Office'), (11, 'Science & Engineering'),
                        (12, 'Sound & Video'), (13, 'Themes & Tweaks'),
                        (14, 'Universal Access')
                    ],
                    default=1,
                    verbose_name='category'
                )),
                ('project', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    to='server.Project',
                    verbose_name='project'
                )),
            ],
            options={
                'verbose_name': 'Application',
                'verbose_name_plural': 'Applications',
                'permissions': (('can_save_application', 'Can save application'),),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='Application',
            unique_together={('name', 'project')},
        ),
    ]
