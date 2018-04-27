# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations
from django.core.management.sql import emit_post_migrate_signal


def add_admin_domain_group(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    emit_post_migrate_signal(2, False, db_alias)
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    group, _ = Group.objects.get_or_create(name='Admin Domain')
    permissions = Permission.objects.filter(codename__in=[
        'add_deployment', 'delete_deployment', 'change_deployment', 'can_save_deployment',
        'add_scope', 'delete_scope', 'change_scope', 'can_save_scope',
        'change_computer', 'can_save_computer',
    ])
    group.permissions.add(*permissions)


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0028_4_16_domains'),
    ]

    operations = [
        migrations.RunPython(add_admin_domain_group),
    ]
