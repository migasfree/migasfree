# -*- coding: UTF-8 -*-

import os
import subprocess
import tempfile

import django.core.management

from StringIO import StringIO

from django.contrib.auth.models import Group, Permission
from django.conf import settings

from migasfree.server.models import UserProfile


def run(cmd):
    out, err = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        shell=True
    ).communicate()

    return out, err


def create_user(name, groups=None):
    if groups is None:
        groups = []

    user = UserProfile.objects.filter(username=name)
    if not user:
        user = UserProfile()
        user.username = name
        user.is_staff = True
        user.is_active = True
        user.is_superuser = (name == 'admin')
        user.set_password(name)
        user.save()

        user.groups.add(*groups)
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


def create_default_users():
    """
    Create default Groups and Users
    """

    # reader group
    reader = Group.objects.filter(name='Reader')
    if not reader:
        reader = Group()
        reader.name = "Reader"
        reader.save()
        tables = [
            "computer", "device", "user", "attribute", "error",
            "fault", "deviceconnection", "devicemanufacturer", "devicemodel",
            "devicetype", "schedule", "scheduledelay", "autocheckerror",
            "faultdefinition", "property", "checking", "project", "pms", "query",
            "package", "deployment", "store", "message", "synchronization",
            "platform", "migration", "notification"
        ]
        add_read_perms(reader, tables)
        reader.save()

    # liberator group
    liberator = Group.objects.filter(name='Liberator')
    if not liberator:
        liberator = Group()
        liberator.name = "Liberator"
        liberator.save()
        tables = ["deployment", "schedule", "scheduledelay"]
        add_all_perms(liberator, tables)
        liberator.save()

    # packager group
    packager = Group.objects.filter(name='Packager')
    if not packager:
        packager = Group()
        packager.name = "Packager"
        packager.save()
        tables = ["package", "store"]
        add_all_perms(packager, tables)
        packager.save()

    # computer checker group
    checker = Group.objects.filter(name='Computer Checker')
    if not checker:
        checker = Group()
        checker.name = "Computer Checker"
        checker.save()
        tables = [
            "autocheckerror", "error", "fault",
            "message", "synchronization", "checking"
        ]
        add_all_perms(checker, tables)
        checker.save()

    # device installer group
    device_installer = Group.objects.filter(name='Device installer')
    if not device_installer:
        device_installer = Group()
        device_installer.name = "Device installer"
        device_installer.save()
        tables = [
            "deviceconnection", "devicemanufacturer",
            "devicemodel", "devicetype"
        ]
        add_all_perms(device_installer, tables)
        device_installer.save()

    # query group
    questioner = Group.objects.filter(name='Query')
    if not questioner:
        questioner = Group()
        questioner.name = "Query"
        questioner.save()
        tables = ["query"]
        add_all_perms(questioner, tables)
        questioner.save()

    # configurator group
    configurator = Group.objects.filter(name='Configurator')
    if not configurator:
        configurator = Group()
        configurator.name = "Configurator"
        configurator.save()
        tables = [
            "checking", "faultdefinition", "property", "pms", "project",
            "message", "update", "platform", "migration",
            "notification"
        ]
        add_all_perms(configurator, tables)
        configurator.save()

    # default users
    create_user("admin")
    create_user("packager", [reader, packager])
    create_user("configurator", [reader, configurator])
    create_user("installer", [reader, device_installer])
    create_user("query", [reader, questioner])
    create_user("liberator", [reader, liberator])
    create_user("checker", [reader, checker])
    create_user("reader", [reader])


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
        _filename = tempfile.mkstemp()[1]
        with open(_filename, "w") as _file:
            _file.write(commands.getvalue())
            _file.flush()

        cmd = "su postgres -c 'psql %s -f %s' -" % (
            settings.DATABASES.get('default').get('NAME'), _filename
        )
        out, err = run(cmd)
        if out != 0:
            print(err)

        os.remove(_filename)


def create_initial_data():
    create_default_users()

    fixtures = [
        'server.checking.json',
        'server.pms.json',
        'server.query.json',
        'server.property.json',
        'server.attribute.json',
        'server.faultdefinition.json',
        'server.schedule.json',
        'server.scheduledelay.json',
        'server.devicetype.json',
        'server.devicefeature.json',
        'server.deviceconnection.json',
    ]
    for fixture in fixtures:
        app, name, ext = fixture.split('.')
        django.core.management.call_command(
            'loaddata',
            os.path.join(
                settings.MIGASFREE_APP_DIR,
                app,
                'fixtures',
                '{0}.{1}'.format(name, ext)
            ),
            interactive=False,
            verbosity=1
        )
