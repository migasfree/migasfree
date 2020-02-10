# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0039_4_19_property_fixtures'),
    ]

    operations = [
        migrations.RunSQL(
            [(
                "UPDATE server_query SET parameters=%s WHERE id=3;",
                [
                    "from migasfree.server.models import Property, Project\n\ndef form_params(request):\n    from migasfree.server.forms import ParametersForm\n    from django import forms\n    class myForm(ParametersForm):\n        property_att = forms.ModelChoiceField(Property.objects.all())\n        project = forms.ModelChoiceField(Project.objects.scope(request.user.userprofile), required=False)\n        value = forms.CharField()\n        exact = forms.ChoiceField(((False,'No'), (True,'Yes')))\n    return myForm",
                ]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_query SET parameters=%s WHERE id=4;",
                [
                    "from migasfree.server.models import Project\n\ndef form_params(request):\n    from migasfree.server.forms import ParametersForm\n    from django import forms\n    class myForm(ParametersForm):\n        project = forms.ModelChoiceField(Project.objects.scope(request.user.userprofile), required=False)\n        package = forms.CharField()\n    return myForm\n",
                ]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_query SET code=%s WHERE id=7;",
                [
                    "from django.utils.translation import ugettext_lazy as _\nfrom datetime import datetime, timedelta, date\nfrom migasfree.server.models import Computer\nlast_days = int(parameters.get('days', 0))\nif last_days <= 0:\n    last_days = 1\ndelta = timedelta(days=1)\nn = date.today() - ((last_days - 1) * delta)\nquery = Computer.productive.scope(request.user.userprofile).select_related('project').filter(created_at__gte=n, created_at__lt=date.today() + delta).order_by('-created_at')\nfields = ('link', 'project', 'created_at', 'ip_address')\ntitles = (_('Computer'), _('Project'), _('Date Input'), _('IP'))",
                ]
            )]
        ),
    ]
