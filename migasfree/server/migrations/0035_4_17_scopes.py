# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0034_4_17_domains_fixtures'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='scope',
            unique_together=set([('name', 'domain', 'user')]),
        ),
    ]
