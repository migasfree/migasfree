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


def configure_user(name, groups=None):
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
    else:
        user = user[0]

    user.groups.clear()
    user.groups.add(*groups)
    user.save()


def add_perms(group, tables=None, all_perms=True):
    if tables is None:
        tables = []

    perms = ['change_{}']
    if all_perms:
        perms.append('add_{}')
        perms.append('delete_{}')
        perms.append('can_save_{}')

    for table in tables:
        app, name = table.split('.')
        for pattern in perms:
            group.permissions.add(
                Permission.objects.get(
                    codename=pattern.format(name),
                    content_type__app_label=app
                ).id
            )

def add_perms_only_modify(group, tables=None):
    if tables is None:
        tables = []

    perms = ['change_{}','can_save_{}']

    for table in tables:
        app, name = table.split('.')
        for pattern in perms:
            group.permissions.add(
                Permission.objects.get(
                    codename=pattern.format(name),
                    content_type__app_label=app
                ).id
            )

def configure_default_users():
    """
    Create/update default Groups and Users
    """

    # reader group
    reader = Group.objects.filter(name='Reader')
    if not reader:
        reader = Group()
        reader.name = "Reader"
        reader.save()
    else:
        reader = reader[0]

    tables = [
        "server.computer", "server.error", "server.fault",
        "server.autocheckerror", "server.notification",
        "server.faultdefinition", "server.synchronization",
        "server.message", "server.migration", "server.statuslog",
        "server.package", "server.deployment", "server.store",
        "server.platform", "server.project", "server.pms",
        "server.schedule", "server.scheduledelay",
        "server.user", "server.userprofile",
        "server.property", "server.attribute", "server.attributeset",
        "server.device", "server.deviceconnection", "server.devicedriver",
        "server.devicefeature", "server.devicelogical",
        "server.devicemanufacturer", "server.devicemodel", "server.devicetype",
        "server.query",
        "server.hwnode", "server.hwcapability",
        "server.hwconfiguration", "server.hwlogicalname",
        "server.domain", "server.scope",
        "catalog.application", "catalog.packagesbyproject",
        "catalog.policy", "catalog.policygroup",
    ]
    reader.permissions.clear()
    add_perms(reader, tables, all_perms=False)
    reader.save()

    # liberator group
    liberator = Group.objects.filter(name='Liberator')
    if not liberator:
        liberator = Group()
        liberator.name = "Liberator"
        liberator.save()
    else:
        liberator = liberator[0]

    tables = [
        "server.deployment", "server.schedule", "server.scheduledelay",
        "catalog.policy", "catalog.policygroup",
        "catalog.application", "catalog.packagesbyproject",
    ]
    liberator.permissions.clear()
    add_perms(liberator, tables)
    liberator.save()

    # packager group
    packager = Group.objects.filter(name='Packager')
    if not packager:
        packager = Group()
        packager.name = "Packager"
        packager.save()
        tables = ["server.package", "server.store"]
        add_perms(packager, tables)
        packager.save()
    else:
        packager = packager[0]

    # computer checker group
    checker = Group.objects.filter(name='Computer Checker')
    if not checker:
        checker = Group()
        checker.name = "Computer Checker"
        checker.save()
    else:
        checker = checker[0]

    tables = [
        "server.autocheckerror", "server.error", "server.fault",
        "server.message", "server.synchronization",
    ]
    checker.permissions.clear()
    add_perms(checker, tables)
    checker.save()

    # device installer group
    device_installer = Group.objects.filter(name='Device installer')
    if not device_installer:
        device_installer = Group()
        device_installer.name = "Device installer"
        device_installer.save()
    else:
        device_installer = device_installer[0]

    tables = [
        "server.device", "server.deviceconnection", "server.devicedriver",
        "server.devicefeature", "server.devicelogical",
        "server.devicemanufacturer", "server.devicemodel", "server.devicetype",
    ]
    device_installer.permissions.clear()
    add_perms(device_installer, tables)
    device_installer.save()

    # query group
    questioner = Group.objects.filter(name='Query')
    if not questioner:
        questioner = Group()
        questioner.name = "Query"
        questioner.save()
    else:
        questioner = questioner[0]

    tables = ["server.query"]
    questioner.permissions.clear()
    add_perms(questioner, tables)
    questioner.save()

    # configurator group
    configurator = Group.objects.filter(name='Configurator')
    if not configurator:
        configurator = Group()
        configurator.name = "Configurator"
        configurator.save()
    else:
        configurator = configurator[0]

    tables = [
        "server.faultdefinition", "server.property",
        "server.pms", "server.project", "server.notification",
        "server.message", "server.synchronization", "server.platform",
        "server.migration", "server.attributeset", "server.autocheckerror",
    ]
    configurator.permissions.clear()
    add_perms(configurator, tables)
    configurator.save()

    # admin domain group
    admin_domain = Group.objects.filter(name='Admin Domain')
    if not admin_domain:
        admin_domain = Group()
        admin_domain.name = "Admin Domain"
        admin_domain.save()
    else:
        admin_domain = admin_domain[0]

    tables = [
        "server.scope", "server.deployment",
    ]
    admin_domain.permissions.clear()
    add_perms(admin_domain, tables)
    add_perms_only_modify(admin_domain, ["server.computer", ])
    admin_domain.save()

    # default users
    configure_user("admin")
    configure_user("admin-domain", [reader, admin_domain] )
    configure_user("packager", [reader, packager])
    configure_user("configurator", [reader, configurator])
    configure_user("installer", [reader, device_installer])
    configure_user("query", [reader, questioner])
    configure_user("liberator", [reader, liberator])
    configure_user("checker", [reader, checker])
    configure_user("reader", [reader])


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
        os.chmod(_filename, 0x777)
        with open(_filename, "w") as _file:
            _file.write(commands.getvalue())
            _file.flush()

        cmd = "PGPASSWORD={} psql -h {} -p {} -U {} -f {}".format(
            settings.DATABASES.get('default').get('PASSWORD'),
            settings.DATABASES.get('default').get('HOST'),
            settings.DATABASES.get('default').get('PORT'),
            settings.DATABASES.get('default').get('USER'),
            _filename
        )
        _, err = run(cmd)
        if err:
            print(err)

        os.remove(_filename)


def create_initial_data():
    configure_default_users()

    fixtures = [
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
                '{0}.{1}.{2}'.format(app, name, ext)
            ),
            interactive=False,
            verbosity=1
        )
