# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations
from django.core.management.sql import emit_post_migrate_signal
from django.contrib.auth.hashers import make_password


def add_migasfree_play_user(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    emit_post_migrate_signal(2, False, db_alias)

    UserProfile = apps.get_model('server', 'UserProfile')
    Permission = apps.get_model('auth', 'Permission')

    name = 'migasfree-play'
    user, _ = UserProfile.objects.using(db_alias).get_or_create(username=name)
    user.is_active = True
    user.password = make_password(name)
    user.save()

    permissions = Permission.objects.using(db_alias).filter(
        codename__in=['change_devicelogical', 'can_save_devicelogical'],
        content_type__app_label='server'
    )
    user.user_permissions.add(*permissions)


def remove_migasfree_play_user(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    emit_post_migrate_signal(2, False, db_alias)

    UserProfile = apps.get_model('server', 'UserProfile')
    user = UserProfile.objects.using(db_alias).get(username='migasfree-play')
    user.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0031_4_17_sources'),
    ]

    operations = [
        migrations.RunPython(add_migasfree_play_user, remove_migasfree_play_user),
    ]
