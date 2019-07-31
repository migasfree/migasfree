# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations
from django.core.management.sql import emit_post_migrate_signal


def fix_domain_admin_group_permissions(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    emit_post_migrate_signal(2, False, db_alias)
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    group = Group.objects.get(name='Domain Admin')
    permissions = Permission.objects.filter(codename__in=[
        'add_deployment', 'delete_deployment', 'change_deployment', 'can_save_deployment',
        'add_scope', 'delete_scope', 'change_scope', 'can_save_scope',
        'add_computer', 'change_computer', 'can_save_computer',
        'add_internalsource', 'delete_internalsource', 'change_internalsource', 'can_save_internalsource',
    ])
    group.permissions.add(*permissions)


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0037_4_17_hardware_node'),
    ]

    operations = [
        migrations.RunPython(fix_domain_admin_group_permissions),
    ]
