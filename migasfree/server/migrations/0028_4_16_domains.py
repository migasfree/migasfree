# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import migasfree.server.models.common


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0027_4_16_fixtures'),
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                )),
                ('name', models.CharField(max_length=50, verbose_name='name', unique=True)),
                ('comment', models.TextField(blank=True, null=True, verbose_name='comment')),
                ('excluded_attributes', models.ManyToManyField(
                    blank=True, related_name='DomainExcludedAttribute',
                    to='server.Attribute', verbose_name='excluded attributes'
                )),
                ('included_attributes', models.ManyToManyField(
                    blank=True, related_name='DomainIncludedAttribute',
                    to='server.Attribute', verbose_name='included attributes'
                )),
                ('tags', models.ManyToManyField(
                    blank=True, related_name='domain_tags',
                    to='server.ServerAttribute', verbose_name='tags'
                )),
            ],
            options={
                'verbose_name': 'Domain',
                'verbose_name_plural': 'Domains',
                'permissions': (('can_save_domain', 'Can save Domain'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='Scope',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                )),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('domain', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='server.Domain', verbose_name='domain'
                )),
                ('excluded_attributes', models.ManyToManyField(
                    blank=True, related_name='ScopeExcludedAttribute',
                    to='server.Attribute', verbose_name='excluded attributes'
                )),
                ('included_attributes', models.ManyToManyField(
                    blank=True, related_name='ScopeIncludedAttribute',
                    to='server.Attribute', verbose_name='included attributes'
                )),
            ],
            options={
                'verbose_name': 'Scope',
                'verbose_name_plural': 'Scopes',
                'permissions': (('can_save_scope', 'Can save Scope'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='project',
        ),
        migrations.AddField(
            model_name='scope',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.UserProfile', verbose_name='user'
            ),
        ),
        migrations.AddField(
            model_name='deployment',
            name='domain',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='server.Domain', verbose_name='domain'
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='domain_preference',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='server.Domain', verbose_name='domain'
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='domains',
            field=models.ManyToManyField(
                blank=True, related_name='domains',
                to='server.Domain', verbose_name='domains'
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='scope_preference',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='server.Scope', verbose_name='Scope'
            ),
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_query SET code=%s, parameters=%s WHERE id=3;",
                [
                    "from migasfree.server.models import Computer, Property, Project\nfrom django.db.models import Count\nquery = Computer.productive.scope(request.user.userprofile).select_related('sync_user').all()\nif parameters['value'] != '':\n    if str(parameters['exact']) == 'True':\n        query = query.filter(sync_attributes__property_att__id=parameters['property_att'], sync_attributes__value=parameters['value'])\n        fld = 'sync_attributes.filter(property_att__id=parameters[\"property_att\"], value=parameters[\"value\"]).values_list(\"value\", flat=True)'\n    else:\n        query = query.filter(sync_attributes__property_att__id=parameters['property_att'], sync_attributes__value__contains=parameters['value'])\n        fld = 'sync_attributes.filter(property_att__id=parameters[\"property_att\"], value__contains=parameters[\"value\"]).values_list(\"value\", flat=True)'\n    if parameters['project']:\n        query = query.select_related('project').filter(project__id=parameters['project'])\nquery = query.annotate(n=Count('id'))\nproperty = Property.objects.get(pk=parameters['property_att'])\nfields = ('link', fld, 'project', 'sync_user.link', 'sync_start_date')\ntitles = ('computer', property.name.lower(), 'project', 'sync user', 'date of login')",
                    "def form_params(request):\n    from migasfree.server.forms import ParametersForm\n    from django import forms\n    class myForm(ParametersForm):\n        property_att = forms.ModelChoiceField(Property.objects.all())\n        project = forms.ModelChoiceField(Project.objects.scope(request.user.userprofile), required=False)\n        value = forms.CharField()\n        exact = forms.ChoiceField(((False,'No'), (True,'Yes')))\n    return myForm",
                ]
            )],
            [(
                "UPDATE server_query SET code=%s, parameters=%s WHERE id=3;",
                [
                    "from migasfree.server.models import Computer, Property, Project\nfrom django.db.models import Count\nquery = Computer.productive.select_related('sync_user').all()\nif parameters['value'] != '':\n    if str(parameters['exact']) == 'True':\n        query = query.filter(sync_attributes__property_att__id=parameters['property_att'], sync_attributes__value=parameters['value'])\n        fld = 'sync_attributes.filter(property_att__id=parameters[\"property_att\"], value=parameters[\"value\"]).values_list(\"value\", flat=True)'\n    else:\n        query = query.filter(sync_attributes__property_att__id=parameters['property_att'], sync_attributes__value__contains=parameters['value'])\n        fld = 'sync_attributes.filter(property_att__id=parameters[\"property_att\"], value__contains=parameters[\"value\"]).values_list(\"value\", flat=True)'\n    if parameters['project']:\n        query = query.select_related('project').filter(project__id=parameters['project'])\nquery = query.annotate(n=Count('id'))\nproperty = Property.objects.get(pk=parameters['property_att'])\nfields = ('link', fld, 'project', 'sync_user.link', 'sync_start_date')\ntitles = ('computer', property.name.lower(), 'project', 'sync user', 'date of login')",
                    "def form_params():\n    from migasfree.server.forms import ParametersForm\n    from django import forms\n    class myForm(ParametersForm):\n        property_att = forms.ModelChoiceField(Property.objects.all())\n        project = forms.ModelChoiceField(Project.objects.all(), required=False)\n        value = forms.CharField()\n        exact = forms.ChoiceField(((False,'No'), (True,'Yes')))\n    return myForm",
                ]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_query SET code=%s, parameters=%s WHERE id=4;",
                [
                    "from migasfree.server.models import Computer\nquery = Computer.productive.scope(request.user.userprofile).select_related('project').filter(software_inventory__contains=parameters['package'])\nif parameters['project']:\n    query = query.filter(project=parameters['project'])\nquery = query.order_by('sync_end_date')\nfields = ('link', 'project.link', 'sync_end_date', 'product')\ntitles = ('Computer', 'Project', 'Last Update', 'Product')",
                    "def form_params(request):\n    from migasfree.server.forms import ParametersForm\n    from django import forms\n    class myForm(ParametersForm):\n        project = forms.ModelChoiceField(Project.objects.scope(request.user.userprofile), required=False)\n        package = forms.CharField()\n    return myForm\n",
                ]
            )],
            [(
                "UPDATE server_query SET code=%s, parameters=%s WHERE id=4;",
                [
                    "from migasfree.server.models import Computer\nquery = Computer.productive.select_related('project').filter(software_inventory__contains=parameters['package'])\nif parameters['project']:\n    query = query.filter(project=parameters['project'])\nquery = query.order_by('sync_end_date')\nfields = ('link', 'project.link', 'sync_end_date', 'product')\ntitles = ('Computer', 'Project', 'Last Update', 'Product')",
                    "def form_params():\n    from migasfree.server.forms import ParametersForm\n    from django import forms\n    class myForm(ParametersForm):\n        project = forms.ModelChoiceField(Project.objects.all(), required=False)\n        package = forms.CharField()\n    return myForm\n",
                ]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_query SET code=%s, parameters=%s WHERE id=7;",
                [
                    "from django.utils.translation import ugettext_lazy as _\nfrom datetime import datetime, timedelta, date\nfrom migasfree.server.models import Computer\nlast_days = parameters['last_days']\nif last_days <= 0 or last_days == '':\n    last_days = 1\nelse:\n    last_days = int(last_days)\ndelta = timedelta(days=1)\nn = date.today() - ((last_days - 1) * delta)\nquery = Computer.productive.scope(request.user.userprofile).select_related('project').filter(created_at__gte=n, created_at__lt=date.today() + delta).order_by('-created_at')\nfields = ('link', 'project', 'created_at', 'ip_address')\ntitles = (_('Computer'), _('Project'), _('Date Input'), _('IP'))",
                    "def form_params(request):\n    from migasfree.server.forms import ParametersForm\n    from django import forms\n    class myForm(ParametersForm):\n        last_days = forms.CharField()\n    return myForm",
                ]
            )],
            [(
                "UPDATE server_query SET code=%s, parameters=%s WHERE id=7;",
                [
                    "from django.utils.translation import ugettext_lazy as _\nfrom datetime import datetime, timedelta, date\nfrom migasfree.server.models import Computer\nlast_days = parameters['last_days']\nif last_days <= 0 or last_days == '':\n    last_days = 1\nelse:\n    last_days = int(last_days)\ndelta = timedelta(days=1)\nn = date.today() - ((last_days - 1) * delta)\nquery = Computer.productive.select_related('project').filter(created_at__gte=n, created_at__lt=date.today() + delta).order_by('-created_at')\nfields = ('link', 'project', 'created_at', 'ip_address')\ntitles = (_('Computer'), _('Project'), _('Date Input'), _('IP'))",
                    "def form_params():\n    from migasfree.server.forms import ParametersForm\n    from django import forms\n    class myForm(ParametersForm):\n        last_days = forms.CharField()\n    return myForm",
                ]
            )]
        ),
    ]
