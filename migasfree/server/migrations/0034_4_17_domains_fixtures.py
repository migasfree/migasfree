# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations
from django.core.management.sql import emit_post_migrate_signal


def add_domain_admin_group(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    emit_post_migrate_signal(2, False, db_alias)
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    group, _ = Group.objects.get_or_create(name='Domain Admin')
    permissions = Permission.objects.filter(codename__in=[
        'add_computer',
    ])
    group.permissions.add(*permissions)


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0033_4_17_pms_fixtures'),
    ]

    operations = [
        migrations.RunPython(add_domain_admin_group),
    ]
