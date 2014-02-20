# -*- coding: UTF-8 -*-

import os
import subprocess

import django.core.management

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from StringIO import StringIO

from migasfree.server.models import UserProfile
from migasfree.settings import DATABASES, MIGASFREE_APP_DIR


def run(cmd_linux):
    (out, err) = subprocess.Popen(cmd_linux,
        stdout=subprocess.PIPE, shell=True).communicate()
    return (out, err)


def create_user(name, groups=[]):
    oUser = UserProfile()
    oUser.username = name
    oUser.is_staff = True
    oUser.is_active = True
    oUser.is_superuser = (name == "admin")
    oUser.save()
    oUser.password = name
    for group in groups:
        oUser.groups.add(group.id)
    oUser.save()


def add_read_perms(group, tables=[]):
    for table in tables:
        group.permissions.add(
            Permission.objects.get(codename="change_%s" % table,
            content_type__app_label="server").id)


def add_all_perms(group, tables=[]):
    for table in tables:
        group.permissions.add(
            Permission.objects.get(codename="add_%s" % table,
            content_type__app_label="server").id)
        group.permissions.add(
            Permission.objects.get(codename="change_%s" % table,
            content_type__app_label="server").id)
        group.permissions.add(
            Permission.objects.get(codename="delete_%s" % table,
            content_type__app_label="server").id)
        group.permissions.add(
            Permission.objects.get(codename="can_save_%s" % table,
            content_type__app_label="server").id)


def create_users():
    """
    Create default Groups and Users
    """

    # GROUP READER
    oGroupRead = Group()
    oGroupRead.name = "Reader"
    oGroupRead.save()
    tables = ["computer", "device", "user", "login", "attribute", "error",
            "fault", "deviceconnection", "devicemanufacturer", "devicemodel",
            "devicetype", "schedule", "scheduledelay", "autocheckerror",
            "faultdef", "property", "checking", "version", "pms", "query",
            "package", "repository", "store", "message", "update",
            "platform", "messageserver", "migration", "notification"]
    add_read_perms(oGroupRead, tables)
    oGroupRead.save()

    # GROUP LIBERATOR
    oGroupRepo = Group()
    oGroupRepo.name = "Liberator"
    oGroupRepo.save()
    tables = ["repository", "schedule", "scheduledelay"]
    add_all_perms(oGroupRepo, tables)
    oGroupRepo.save()

    # GROUP PACKAGER
    oGroupPackager = Group()
    oGroupPackager.name = "Packager"
    oGroupPackager.save()
    tables = ["package", "store"]
    add_all_perms(oGroupPackager, tables)
    oGroupPackager.save()

    # GROUP COMPUTER CHECKER
    oGroupCheck = Group()
    oGroupCheck.name = "Computer Checker"
    oGroupCheck.save()
    tables = ["autocheckerror", "error", "fault", "message", "update"]
    add_all_perms(oGroupCheck, tables)
    oGroupCheck.save()

    # GROUP DEVICE INSTALLER
    oGroupDev = Group()
    oGroupDev.name = "Device installer"
    oGroupDev.save()
    tables = ["deviceconnection", "devicemanufacturer", "devicemodel",
            "devicetype"]
    add_all_perms(oGroupDev, tables)
    oGroupDev.save()

    # GROUP QUERY
    oGroupQuery = Group()
    oGroupQuery.name = "Query"
    oGroupQuery.save()
    tables = ["query"]
    add_all_perms(oGroupQuery, tables)
    oGroupQuery.save()

    # GROUP CONFIGURATOR
    oGroupSys = Group()
    oGroupSys.name = "Configurator"
    oGroupSys.save()
    tables = ["checking", "faultdef", "property", "pms", "version",
            "message", "update", "platform", "messageserver", "migration",
            "notification"]
    add_all_perms(oGroupSys, tables)
    oGroupSys.save()

    # CREATE DEFAULT USERS
    create_user("admin")
    create_user("packager", [oGroupRead, oGroupPackager])
    create_user("configurator", [oGroupRead, oGroupSys])
    create_user("installer", [oGroupRead, oGroupDev])
    create_user("query", [oGroupRead, oGroupQuery])
    create_user("liberator", [oGroupRead, oGroupRepo])
    create_user("checker", [oGroupRead, oGroupCheck])
    create_user("reader", [oGroupRead])


def sequence_reset():
    commands = StringIO()

    os.environ['DJANGO_COLORS'] = 'nocolor'
    django.core.management.call_command(
        'sqlsequencereset',
        'server',
        stdout=commands
    )

    if DATABASES.get('default').get('ENGINE') == \
    'django.db.backends.postgresql_psycopg2':
        cfile = "/tmp/migasfree.sequencereset.sql"  # FIXME tmpfile
        with open(cfile, "w") as ofile:
            ofile.write(commands.getvalue())
            ofile.flush()
            cmd_linux = "su postgres -c 'psql migasfree -f " + cfile + "' -"
            (out, err) = run(cmd_linux)

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
    ]
    for fixture in fixtures:
        django.core.management.call_command(
            'loaddata',
            os.path.join(
                MIGASFREE_APP_DIR,
                "server",
                "fixtures",
                fixture
            ),
            verbosity=1
        )
