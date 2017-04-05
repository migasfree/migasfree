# -*- coding: UTF-8 -*-

import os
import subprocess

import django.core.management

from StringIO import StringIO

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.conf import settings

from migasfree.server.models import UserProfile


def run(cmd_linux):
    (out, err) = subprocess.Popen(
        cmd_linux,
        stdout=subprocess.PIPE,
        shell=True
    ).communicate()

    return out, err


def create_user(name, groups=None):
    if groups is None:
        groups = []

    user = UserProfile()
    user.username = name
    user.is_staff = True
    user.is_active = True
    user.is_superuser = (name == "admin")
    user.save()
    user.password = name
    for group in groups:
        user.groups.add(group.id)
    user.save()


def add_read_perms(group, tables=None):
    if tables is None:
        tables = []

    for table in tables:
        group.permissions.add(
            Permission.objects.get(
                codename="change_%s" % table,
                content_type__app_label="server"
            ).id
        )


def add_all_perms(group, tables=None):
    if tables is None:
        tables = []

    perms = ['add_%s', 'change_%s', 'delete_%s', 'can_save_%s']
    for table in tables:
        for pattern in perms:
            group.permissions.add(
                Permission.objects.get(
                    codename=pattern % table,
                    content_type__app_label='server'
                ).id
            )


def create_users():
    """
    Create default Groups and Users
    """

    read_group = Group()
    read_group.name = "Reader"
    read_group.save()
    tables = [
        "computer", "device", "user", "attribute", "error",
        "fault", "deviceconnection", "devicemanufacturer", "devicemodel",
        "devicetype", "schedule", "scheduledelay", "autocheckerror",
        "faultdefinition", "property", "checking", "version", "pms", "query",
        "package", "deployment", "store", "message", "synchronization",
        "platform", "messageserver", "migration", "notification"
    ]
    add_read_perms(read_group, tables)
    read_group.save()

    deploy_group = Group()
    deploy_group.name = "Liberator"
    deploy_group.save()
    tables = ["deployment", "schedule", "scheduledelay"]
    add_all_perms(deploy_group, tables)
    deploy_group.save()

    packager_group = Group()
    packager_group.name = "Packager"
    packager_group.save()
    tables = ["package", "store"]
    add_all_perms(packager_group, tables)
    packager_group.save()

    checker_group = Group()
    checker_group.name = "Computer Checker"
    checker_group.save()
    tables = [
        "autocheckerror", "error", "fault",
        "message", "synchronization", "checking"
    ]
    add_all_perms(checker_group, tables)
    checker_group.save()

    device_installer_group = Group()
    device_installer_group.name = "Device installer"
    device_installer_group.save()
    tables = [
        "deviceconnection", "devicemanufacturer", "devicemodel", "devicetype"
    ]
    add_all_perms(device_installer_group, tables)
    device_installer_group.save()

    query_group = Group()
    query_group.name = "Query"
    query_group.save()
    tables = ["query"]
    add_all_perms(query_group, tables)
    query_group.save()

    configurator_group = Group()
    configurator_group.name = "Configurator"
    configurator_group.save()
    tables = [
        "checking", "faultdefinition", "property", "pms", "version",
        "message", "update", "platform", "messageserver", "migration",
        "notification"
    ]
    add_all_perms(configurator_group, tables)
    configurator_group.save()

    # default users
    create_user("admin")
    create_user("packager", [read_group, packager_group])
    create_user("configurator", [read_group, configurator_group])
    create_user("installer", [read_group, device_installer_group])
    create_user("query", [read_group, query_group])
    create_user("liberator", [read_group, deploy_group])
    create_user("checker", [read_group, checker_group])
    create_user("reader", [read_group])


def sequence_reset():
    commands = StringIO()

    os.environ['DJANGO_COLORS'] = 'nocolor'
    django.core.management.call_command(
        'sqlsequencereset',
        'server',
        stdout=commands
    )

    if settings.DATABASES.get('default').get('ENGINE') == \
            'django.db.backends.postgresql_psycopg2':
        cfile = "/tmp/migasfree.sequencereset.sql"  # FIXME tmpfile
        with open(cfile, "w") as ofile:
            ofile.write(commands.getvalue())
            ofile.flush()

        cmd_linux = "su postgres -c 'psql migasfree -f %s' -" % cfile
        run(cmd_linux)

        os.remove(cfile)


def create_registers():
    """
    Load default data
    """
    create_users()

    # Load Fixtures
    fixtures = [
        'server.checking.json',
        'server.pms.json',
        'server.query.json',
        'server.property.json',
        'server.attribute.json',
        'server.faultdef.json',
        'server.schedule.json',
        'server.scheduledelay.json',
        'server.devicetype.json',
        'server.devicefeature.json',
        'server.deviceconnection.json',
    ]
    for fixture in fixtures:
        django.core.management.call_command(
            'loaddata',
            os.path.join(
                settings.MIGASFREE_APP_DIR,
                "server",
                "fixtures",
                fixture
            ),
            verbosity=1
        )
