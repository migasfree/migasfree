# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0005_4_12_changes'),
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='devicedriver',
            options={
                'ordering': ['model', 'name'],
                'permissions': (('can_save_devicedriver', 'Can save Device Driver'),),
                'verbose_name': 'Driver', 'verbose_name_plural': 'Drivers'
            },
        ),
        migrations.AlterModelOptions(
            name='devicemanufacturer',
            options={
                'ordering': ['name'],
                'permissions': (('can_save_devicemanufacturer', 'Can save Device Manufacturer'),),
                'verbose_name': 'Manufacturer', 'verbose_name_plural': 'Manufacturers'
            },
        ),
        migrations.AlterModelOptions(
            name='devicemodel',
            options={
                'ordering': ['manufacturer', 'name'],
                'permissions': (('can_save_devicemodel', 'Can save Device Model'),),
                'verbose_name': 'Model', 'verbose_name_plural': 'Models'
            },
        ),
        migrations.AlterModelOptions(
            name='faultdef',
            options={
                'ordering': ['name'],
                'permissions': (('can_save_faultdef', 'Can save Fault Definition'),),
                'verbose_name': 'Fault Definition', 'verbose_name_plural': 'Fault Definitions'
            },
        ),
        migrations.AlterModelOptions(
            name='attribute',
            options={
                'ordering': ['property_att__prefix', 'value'],
                'permissions': (('can_save_attribute', 'Can save Attribute'),),
                'verbose_name': 'Attribute/Tag', 'verbose_name_plural': 'Attributes/Tags'
            },
        ),
        migrations.AlterModelOptions(
            name='property',
            options={
                'ordering': ['name'],
                'permissions': (('can_save_property', 'Can save Property'),),
                'verbose_name': 'Property/TagType', 'verbose_name_plural': 'Properties/TagTypes'
            },
        ),
        migrations.AlterModelOptions(
            name='version',
            options={
                'ordering': ['name'],
                'permissions': (('can_save_version', 'Can save Version'),),
                'verbose_name': 'Version', 'verbose_name_plural': 'Versions'
            },
        ),
        migrations.AlterModelOptions(
            name='repository',
            options={
                'ordering': ['version__name', 'name'],
                'permissions': (('can_save_repository', 'Can save Repository'),),
                'verbose_name': 'Repository', 'verbose_name_plural': 'Repositories'
            },
        ),
        migrations.AlterModelOptions(
            name='store',
            options={
                'ordering': ['name', 'version'],
                'permissions': (('can_save_store', 'Can save Store'),),
                'verbose_name': 'Store', 'verbose_name_plural': 'Stores'
            },
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_checking SET code=%s WHERE id=10;",
                ["import os\nfrom migasfree.settings import MIGASFREE_REPO_DIR\nurl = '#'\nalert = 'info'\ntarget = 'server'\nresult = 0\nmsg = ''\nif os.path.exists(MIGASFREE_REPO_DIR):\n    for _version in os.listdir(MIGASFREE_REPO_DIR):\n        _repos = os.path.join(MIGASFREE_REPO_DIR, _version, 'TMP/REPOSITORIES/dists')\n        if os.path.exists(_repos):\n            for _repo in os.listdir(_repos):\n                result += 1\n                msg += '%s en %s.' % (_repo, _version)\nmsg = 'Creating %s repositories: %s' % (result, msg)"]
            )],
            migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_checking SET code=%s, name=%s WHERE id=3;",
                [
                    "from migasfree.server.models import Package\nresult = Package.objects.filter(repository__id__exact=None).count()\nurl = '/admin/server/package/?repository__isnull=True'\nalert = 'warning'\nmsg = 'Package/Set orphan'\ntarget = 'server'\n",
                    "Orphaned Package/Set"
                ]
            )],
            [(
                "UPDATE server_checking SET code=%s WHERE id=3;",
                ["from migasfree.server.models import Package\nfrom django.db.models import Q\nresult = Package.objects.filter(Q(repository__id__exact=None)).count()\nurl = '/query/5/'\nalert = 'warning'\nmsg = 'Package/Set orphan'\ntarget = 'server'\n"]
            )]
        ),
        migrations.RunSQL(
            "DELETE FROM server_query WHERE id=1;",
            migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            "DELETE FROM server_query WHERE id=2;",
            [(
                "INSERT INTO server_query (id, code, name, parameters, description) VALUES (%d, %s, %s, %s, %s);",
                [
                    2,
                    "from django.utils.translation import ugettext_lazy as _\nfrom migasfree.server.models import Package\nquery = Package.objects.filter(name__contains=parameters['name'])\nfields = ('link', 'store')\ntitles = (_('Name'), _('Store'))\n",
                    "Packages/Sets...",
                    "def form_params():\n    from migasfree.server.forms import ParametersForm\n    from django import forms\n    class myForm(ParametersForm):\n        name = forms.CharField()\n    return myForm\n",
                    "Package/Set List"
                ]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_query SET code=%s WHERE id=4;",
                ["from migasfree.server.models import Computer\nquery = Computer.productives.select_related('version').filter(software__contains=parameters['package']).order_by('datelastupdate')\nfields = ('link', 'version.link', 'datelastupdate', 'product')\ntitles = ('Computer', 'Version', 'Last Update', 'Product')"]
            )],
            migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            "DELETE FROM server_query WHERE id=5;",
            [(
                "INSERT INTO server_query (id, code, name, parameters, description) VALUES (%d, %s, %s, %s, %s);",
                [
                    5,
                    "from django.utils.translation import ugettext_lazy as _\nfrom migasfree.server.models import Package\nquery = Package.objects.filter(repository__id__exact=None)\nfields = ('version.name', 'store.name', 'link')\ntitles = (_('Version'), _('Store'), _('Package/Set'))\n",
                    "Package/Set Orphan",
                    "",
                    "Packages/Sets that have not been assigned to any repository"
                ]
            )]
        ),
        migrations.RunSQL(
            "DELETE FROM server_query WHERE id=6;",
            [(
                "INSERT INTO server_query (id, code, name, parameters, description) VALUES (%d, %s, %s, %s, %s);",
                [
                    6,
                    "from django.utils.translation import ugettext_lazy as _\nfrom migasfree.server.models import Repository\nquery = Repository.objects.select_related('version').filter(packages__name__contains=parameters['package']).distinct()\nfields = ('link', 'packages_link')\ntitles = (_('Repository'), _('Packages'))\n",
                    "Repositories with a Package/Set...",
                    "def form_params():\n    from migasfree.server.forms import ParametersForm\n    from django import forms\n    class myForm(ParametersForm):\n        package = forms.CharField()\n    return myForm\n",
                    "Repository list that have assigned a certain Package/Set"
                ]
            )]
        ),
    ]
