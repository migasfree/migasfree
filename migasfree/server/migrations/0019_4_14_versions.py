# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0018_4_14_properties'),
    ]

    operations = [
        migrations.RenameModel(old_name='Version', new_name='Project'),
        migrations.RemoveField(model_name='Project', name='computerbase'),
        migrations.RemoveField(model_name='Project', name='base'),
        migrations.RenameField(
            model_name='Project',
            old_name='autoregister',
            new_name='auto_register_computers'
        ),
        migrations.AlterField(
            model_name='Project',
            name='auto_register_computers',
            field=models.BooleanField(
                default=False,
                help_text='Is not needed a user for register computers in database and get the keys.',
                verbose_name='auto register computers'
            ),
        ),
        migrations.AlterModelOptions(
            name='Project',
            options={
                'ordering': ['name'],
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
                'permissions': (('can_save_project', 'Can save Project'),),
            },
        ),
        migrations.RenameField(
            model_name='Deployment',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Deployment',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.AlterModelOptions(
            name='deployment',
            options={
                'ordering': ['project__name', 'name'],
                'permissions': (('can_save_deployment', 'Can save Deployment'),),
                'verbose_name': 'Deployment',
                'verbose_name_plural': 'Deployments'
            },
        ),
        migrations.AlterUniqueTogether(
            name='deployment',
            unique_together={('name', 'project')},
        ),
        migrations.RenameField(
            model_name='Store',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Store',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.AlterModelOptions(
            name='Store',
            options={
                'ordering': ['name', 'project'],
                'permissions': (('can_save_store', 'Can save Store'),),
                'verbose_name': 'Store',
                'verbose_name_plural': 'Stores'
            },
        ),
        migrations.RenameField(
            model_name='Computer',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Computer',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.RenameField(
            model_name='Error',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Error',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.RenameField(
            model_name='Fault',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Fault',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.RenameField(
            model_name='Migration',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Migration',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.RenameField(
            model_name='Synchronization',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Synchronization',
            name='project',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.RenameField(
            model_name='UserProfile',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='UserProfile',
            name='project',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.AlterField(
            model_name='query',
            name='code',
            field=models.TextField(
                blank=True,
                default=b"query = Package.objects.filter(project=PROJECT).filter(deployment__id__exact=None)\nfields = ('id', 'name', 'store__name')\ntitles = ('id', 'name', 'store')",
                help_text='Django Code: project = user.project, query = QuerySet, fields = list of QuerySet fields names to show, titles = list of QuerySet fields titles',
                null=True,
                verbose_name='code'
            ),
        ),
        migrations.RenameField(
            model_name='DeviceDriver',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='DeviceDriver',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.AlterUniqueTogether(
            name='DeviceDriver',
            unique_together={('model', 'project', 'feature')},
        ),
        migrations.RenameField(
            model_name='Package',
            old_name='version',
            new_name='project'
        ),
        migrations.AlterField(
            model_name='Package',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Project',
                verbose_name='project'
            ),
        ),
        migrations.AlterUniqueTogether(
            name='package',
            unique_together={('name', 'project')},
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_property SET name=%s, prefix=%s WHERE id=4;",
                [
                    "PROJECT",
                    "PRJ"
                ]
            )],
            [(
                "UPDATE server_property SET name=%s, prefix=%s WHERE id=4;",
                [
                    "VERSION",
                    "VER"
                ]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_checking SET code=%s WHERE id=10;",
                [
                    "import os\nfrom migasfree.settings import MIGASFREE_PUBLIC_DIR\nurl = '#'\nalert = 'info'\ntarget = 'server'\nresult = 0\nmsg = ''\nif os.path.exists(MIGASFREE_PUBLIC_DIR):\n    for _project in os.listdir(MIGASFREE_PUBLIC_DIR):\n        _repos = os.path.join(MIGASFREE_PUBLIC_DIR, _project, 'TMP/REPOSITORIES/dists')\n        if os.path.exists(_repos):\n            for _repo in os.listdir(_repos):\n                result += 1\n                msg += '%s at %s.' % (_repo, _project)\nmsg = 'Creating %s repositories: %s' % (result, msg)"
                ]
            )],
            migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_query SET code=%s, parameters=%s WHERE id=3;",
                [
                    "from migasfree.server.models import Computer, Property, Project\nfrom django.db.models import Count\nquery = Computer.productive.select_related('sync_user').all()\nif parameters['value'] != '':\n    if str(parameters['exact']) == 'True':\n        query = query.filter(sync_attributes__property_att__id=parameters['property_att'], sync_attributes__value=parameters['value'])\n        fld = 'sync_attributes.filter(property_att__id=parameters[\"property_att\"], value=parameters[\"value\"]).values_list(\"value\", flat=True)'\n    else:\n        query = query.filter(sync_attributes__property_att__id=parameters['property_att'], sync_attributes__value__contains=parameters['value'])\n        fld = 'sync_attributes.filter(property_att__id=parameters[\"property_att\"], value__contains=parameters[\"value\"]).values_list(\"value\", flat=True)'\n    if parameters['project']:\n        query = query.select_related('project').filter(project__id=parameters['project'])\nquery = query.annotate(n=Count('id'))\nproperty = Property.objects.get(pk=parameters['property_att'])\nfields = ('link', fld, 'project', 'sync_user.link', 'sync_start_date')\ntitles = ('computer', property.name.lower(), 'project', 'sync user', 'date of login')",
                    "def form_params():\n    from migasfree.server.forms import ParametersForm\n    from django import forms\n    class myForm(ParametersForm):\n        property_att = forms.ModelChoiceField(Property.objects.all())\n        project = forms.ModelChoiceField(Project.objects.all())\n        value = forms.CharField()\n        exact = forms.ChoiceField( ((False,'No'),(True,'Yes')) )\n    return myForm"
                ]
            )],
            [(
                "UPDATE server_query SET code=%s, parameters=%s WHERE id=3;",
                [
                    "from migasfree.server.models import Computer, Property, Version\nfrom django.db.models import Count\nquery = Computer.productive.select_related('sync_user').all()\nif parameters['value'] != '':\n    if str(parameters['exact']) == 'True':\n        query = query.filter(sync_attributes__property_att__id=parameters['property_att'], sync_attributes__value=parameters['value'])\n        fld = 'sync_attributes.filter(property_att__id=parameters[\"property_att\"], value=parameters[\"value\"]).values_list(\"value\", flat=True)'\n    else:\n        query = query.filter(sync_attributes__property_att__id=parameters['property_att'], sync_attributes__value__contains=parameters['value'])\n        fld = 'sync_attributes.filter(property_att__id=parameters[\"property_att\"], value__contains=parameters[\"value\"]).values_list(\"value\", flat=True)'\n    if parameters['version']:\n        query = query.select_related('version').filter(version__id=parameters['version'])\nquery = query.annotate(n=Count('id'))\nproperty = Property.objects.get(pk=parameters['property_att'])\nfields = ('link', fld, 'version', 'sync_user.link', 'sync_start_date')\ntitles = ('computer', property.name.lower(), 'version', 'sync user', 'date of login')",
                    "def form_params():\n    from migasfree.server.forms import ParametersForm\n    from django import forms\n    class myForm(ParametersForm):\n        property_att = forms.ModelChoiceField(Property.objects.all())\n        version = forms.ModelChoiceField(Version.objects.all())\n        value = forms.CharField()\n        exact = forms.ChoiceField( ((False,'No'),(True,'Yes')) )\n    return myForm"
                ]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_query SET code=%s WHERE id=4;",
                [
                    "from migasfree.server.models import Computer\nquery = Computer.productive.select_related('project').filter(software_inventory__contains=parameters['package']).order_by('sync_end_date')\nfields = ('link', 'project.link', 'sync_end_date', 'product')\ntitles = ('Computer', 'Project', 'Last Update', 'Product')"
                ]
            )],
            [(
                "UPDATE server_query SET code=%s WHERE id=4;",
                [
                    "from migasfree.server.models import Computer\nquery = Computer.productive.select_related('version').filter(software_inventory__contains=parameters['package']).order_by('sync_end_date')\nfields = ('link', 'version.link', 'sync_end_date', 'product')\ntitles = ('Computer', 'Version', 'Last Update', 'Product')"
                ]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_query SET code=%s WHERE id=7;",
                [
                    "from django.utils.translation import ugettext_lazy as _\nfrom datetime import datetime, timedelta, date\nfrom migasfree.server.models import Computer\nlast_days = parameters['last_days']\nif last_days <= 0 or last_days == '':\n    last_days = 1\nelse:\n    last_days = int(last_days)\ndelta = timedelta(days=1)\nn = date.today() - ((last_days - 1) * delta)\nquery = Computer.productive.select_related('project').filter(created_at__gte=n, created_at__lt=date.today() + delta).order_by('-created_at')\nfields = ('link', 'project', 'created_at', 'ip_address')\ntitles = (_('Computer'), _('Project'), _('Date Input'), _('IP'))"
                ]
            )],
            [(
                "UPDATE server_query SET code=%s WHERE id=7;",
                [
                    "from django.utils.translation import ugettext_lazy as _\nfrom datetime import datetime, timedelta, date\nfrom migasfree.server.models import Computer\nlast_days = parameters['last_days']\nif last_days <= 0 or last_days == '':\n    last_days = 1\nelse:\n    last_days = int(last_days)\ndelta = timedelta(days=1)\nn = date.today() - ((last_days - 1) * delta)\nquery = Computer.productive.select_related('version').filter(created_at__gte=n, created_at__lt=date.today() + delta).order_by('-created_at')\nfields = ('link', 'version', 'created_at', 'ip_address')\ntitles = (_('Computer'), _('Version'), _('Date Input'), _('IP'))"
                ]
            )]
        ),
    ]
