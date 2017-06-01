# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models


def sort_properties(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    Property = apps.get_model('server', 'Property')
    basic = ['SET', 'CID', 'PLT', 'VER', 'IP', 'USR']

    for item in Property.objects.using(db_alias):
        if item.prefix in basic:
            item.sort = 'basic'
            item.code = ''
        elif item.tag:
            item.sort = 'server'
            item.code = ''
        elif not item.tag:
            item.sort = 'client'

        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0017_4_14_checkings_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='BasicProperty',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': 'Basic Property',
                'verbose_name_plural': 'Basic Properties',
            },
            bases=('server.property',),
        ),
        migrations.RenameModel(
            old_name='TagType',
            new_name='ServerProperty',
        ),
        migrations.AlterModelOptions(
            name='ServerProperty',
            options={
                'proxy': True,
                'verbose_name': 'Tag Category',
                'verbose_name_plural': 'Tag Categories',
            },
        ),
        migrations.AlterModelOptions(
            name='ClientProperty',
            options={
                'verbose_name': 'Formula',
                'verbose_name_plural': 'Formulas'
            },
        ),
        migrations.AlterModelOptions(
            name='property',
            options={
                'ordering': ['name'],
                'permissions': (('can_save_property', 'Can save Property'),),
                'verbose_name': 'Property',
                'verbose_name_plural': 'Properties'
            },
        ),
        migrations.RenameField(
            model_name='property',
            old_name='active',
            new_name='enabled',
        ),
        migrations.AlterField(
            model_name='property',
            name='enabled',
            field=models.BooleanField(default=True, verbose_name='enabled'),
        ),
        migrations.RenameField(
            model_name='property',
            old_name='auto',
            new_name='auto_add',
        ),
        migrations.AlterField(
            model_name='property',
            name='auto_add',
            field=models.BooleanField(
                default=True,
                help_text='automatically add the attribute to database',
                verbose_name='automatically add'
            ),
        ),
        migrations.AlterField(
            model_name='property',
            name='code',
            field=models.TextField(
                blank=True,
                help_text="This code will execute in the client computer, and it must put in the standard output the value of the attribute correspondent to this property.<br>The format of this value is 'name~description', where 'description' is optional.<br><b>Example of code:</b><br>#Create an attribute with the name of computer from bash<br> echo $HOSTNAME",
                null=True,
                verbose_name='code'
            ),
        ),
        migrations.AlterField(
            model_name='property',
            name='language',
            field=models.IntegerField(
                choices=[
                    (0, b'bash'),
                    (1, b'python'),
                    (2, b'perl'),
                    (3, b'php'),
                    (4, b'ruby'),
                    (5, b'cmd'),
                    (6, b'powershell')
                ],
                default=0,
                verbose_name='programming language'
            )
        ),
        migrations.AlterField(
            model_name='property',
            name='kind',
            field=models.CharField(
                choices=[
                    (b'N', 'Normal'),
                    (b'-', 'List'),
                    (b'L', 'Added to the left'),
                    (b'R', 'Added to the right')
                ],
                default=b'N',
                max_length=1,
                verbose_name='kind'
            ),
        ),
        migrations.AddField(
            model_name='property',
            name='sort',
            field=models.CharField(
                choices=[
                    (b'basic', 'Basic'),
                    (b'client', 'Client'),
                    (b'server', 'Server')
                ],
                default=b'client',
                max_length=10,
                verbose_name='sort'
            ),
        ),
        migrations.RunPython(
            sort_properties,
            migrations.RunPython.noop
        ),
        migrations.RemoveField(
            model_name='property',
            name='tag',
        ),
        migrations.CreateModel(
            name='BasicAttribute',
            fields=[
            ],
            options={
                'verbose_name': 'Basic Attribute',
                'proxy': True,
                'verbose_name_plural': 'Basic Attributes',
            },
            bases=('server.attribute',),
        ),
        migrations.AlterModelOptions(
            name='attribute',
            options={
                'ordering': ['property_att__prefix', 'value'],
                'permissions': (('can_save_attribute', 'Can save Attribute'),),
                'verbose_name': 'Attribute',
                'verbose_name_plural': 'Attributes'
            },
        ),
        migrations.AlterModelOptions(
            name='feature',
            options={
                'verbose_name': 'Feature',
                'verbose_name_plural': 'Features'
            },
        ),
        migrations.RenameModel(
            old_name='Feature',
            new_name='ClientAttribute',
        ),
        migrations.RenameModel(
            old_name='Tag',
            new_name='ServerAttribute',
        ),
        migrations.AlterModelOptions(
            name='ClientAttribute',
            options={
                'verbose_name': 'Attribute',
                'verbose_name_plural': 'Attributes'
            },
        ),
        migrations.AlterField(
            model_name='computer',
            name='tags',
            field=models.ManyToManyField(
                blank=True,
                related_name='tags',
                to='server.ServerAttribute',
                verbose_name='tags'
            ),
        ),
    ]
