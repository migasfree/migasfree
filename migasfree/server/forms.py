# -*- coding: utf-8 -*-

from django import forms

class ParametersForm(forms.Form):
    id_query = forms.CharField(required=True, widget=forms.HiddenInput())
    user_version = forms.CharField(required=True, widget=forms.HiddenInput())
