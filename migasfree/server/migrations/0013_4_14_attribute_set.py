# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-04-03 14:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0012_4_14_fault_definitions'),
    ]

    operations = [
        migrations.RenameField(
            model_name='AttributeSet',
            old_name='active',
            new_name='enabled',
        ),
        migrations.AlterField(
            model_name='AttributeSet',
            name='enabled',
            field=models.BooleanField(default=True, verbose_name='enabled'),
        ),
        migrations.RenameField(
            model_name='AttributeSet',
            old_name='attributes',
            new_name='included_attributes',
        ),
        migrations.AlterField(
            model_name='AttributeSet',
            name='included_attributes',
            field=models.ManyToManyField(
                blank=True, to='server.Attribute',
                verbose_name='included attributes'
            ),
        ),
        migrations.RenameField(
            model_name='AttributeSet',
            old_name='excludes',
            new_name='excluded_attributes',
        ),
        migrations.AlterField(
            model_name='AttributeSet',
            name='excluded_attributes',
            field=models.ManyToManyField(
                blank=True,
                related_name='ExcludedAttributesGroup',
                to='server.Attribute',
                verbose_name='excluded attributes'
            ),
        ),
        migrations.AddField(
            model_name='AttributeSet',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AlterModelOptions(
            name='AttributeSet',
            options={
                'permissions': (('can_save_attributeset', 'Can save Attributes Set'),),
                'verbose_name': 'Attribute Set',
                'verbose_name_plural': 'Attribute Sets'
            },
        ),
    ]
