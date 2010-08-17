from django import forms

from migasfree.system.models import Computer
from migasfree.system.models import User
from migasfree.system.models import Query


class ParametersForm(forms.Form):
    id_query = forms.CharField(required=True,widget=forms.HiddenInput())
    user_version = forms.CharField(required=True,widget=forms.HiddenInput())






