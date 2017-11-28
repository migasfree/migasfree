# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from form_utils.widgets import ImageWidget

from migasfree.server.fields import MigasAutoCompleteSelectMultipleField

from .models import Application, Policy, PolicyGroup


class ApplicationForm(forms.ModelForm):
    available_for_attributes = MigasAutoCompleteSelectMultipleField(
        'attribute', required=False,
        label=_('available for attributes'), show_help_text=False
    )

    class Meta:
        model = Application
        fields = '__all__'
        widgets = {
            'icon': ImageWidget
        }


class PolicyForm(forms.ModelForm):
    included_attributes = MigasAutoCompleteSelectMultipleField(
        'attribute', required=False,
        label=_('included attributes'), show_help_text=False
    )
    excluded_attributes = MigasAutoCompleteSelectMultipleField(
        'attribute', required=False,
        label=_('excluded attributes'), show_help_text=False
    )

    class Meta:
        model = Policy
        fields = '__all__'


class PolicyGroupForm(forms.ModelForm):
    included_attributes = MigasAutoCompleteSelectMultipleField(
        'attribute', required=False,
        label=_('included attributes'), show_help_text=False
    )
    excluded_attributes = MigasAutoCompleteSelectMultipleField(
        'attribute', required=False,
        label=_('excluded attributes'), show_help_text=False
    )
    applications = MigasAutoCompleteSelectMultipleField(
        'application', required=False,
        label=_('application'), show_help_text=False
    )

    class Meta:
        model = PolicyGroup
        fields = '__all__'
