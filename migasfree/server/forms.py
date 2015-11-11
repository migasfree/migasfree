# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from ajax_select import make_ajax_form, make_ajax_field

from migasfree.middleware import threadlocals
from .models import (
    Repository, UserProfile, Computer, DeviceLogical,
    Property, Tag
)


class ParametersForm(forms.Form):
    id_query = forms.CharField(required=True, widget=forms.HiddenInput())
    user_version = forms.CharField(required=True, widget=forms.HiddenInput())


class RepositoryForm(forms.ModelForm):
    attributes = make_ajax_field(Repository, 'attributes', 'attribute')
    packages = make_ajax_field(Repository, 'packages', 'package')
    excludes = make_ajax_field(Repository, 'excludes', 'attribute')

    class Meta:
        model = Repository

    def __init__(self, *args, **kwargs):
        super(RepositoryForm, self).__init__(*args, **kwargs)
        try:
            self.fields['version'].initial = UserProfile.objects.get(
                pk=threadlocals.get_current_user().id
            ).version.id
        except UserProfile.DoesNotExist:
            pass


class DeviceLogicalForm(forms.ModelForm):
    x = make_ajax_form(Computer, {'devices_logical': 'computer'})

    computers = x.devices_logical
    computers.label = _('Computers')

    class Meta:
        model = DeviceLogical

    def __init__(self, *args, **kwargs):
        super(DeviceLogicalForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            lst = []
            for computer in self.instance.computer_set.all():
                lst.append(computer.id)
            self.fields['computers'].initial = lst

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)
        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            instance.computer_set.clear()
            for computer in self.cleaned_data['computers']:
                instance.computer_set.add(computer)

        self.save_m2m = save_m2m
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class PropertyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PropertyForm, self).__init__(*args, **kwargs)

        self.fields['code'].required = True

    class Meta:
        model = Property


class TagForm(forms.ModelForm):
    x = make_ajax_form(Computer, {'tags': 'computer'})

    computers = x.tags
    computers.label = _('Computers')

    class Meta:
        model = Tag

    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            lst = []
            for computer in self.instance.computer_set.all():
                lst.append(computer.id)
            self.fields['computers'].initial = lst

        self.fields['property_att'].queryset = Property.objects.filter(tag=True)

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)
        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            instance.computer_set.clear()
            for computer in self.cleaned_data['computers']:
                instance.computer_set.add(computer)

        self.save_m2m = save_m2m
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ComputerForm(forms.ModelForm):
    devices_logical = make_ajax_field(
        Computer, 'devices_logical', 'devicelogical'
    )
    tags = make_ajax_field(Computer, 'tags', 'tag')

    class Meta:
        model = Computer

    def clean(self):
        super(ComputerForm, self).clean()
        errors = []
        if self.cleaned_data.get('status') == 'available':
            if self.cleaned_data.get('tags') != []:
                errors.append(_("Status available can not have tags"))
            if self.cleaned_data.get('devices_logical') != []:
                errors.append(_("Status available can not have devices logical"))

        if errors:
            raise forms.ValidationError(errors)

        return self.cleaned_data


class ExtraThinTextarea(forms.Textarea):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', {})
        attrs.setdefault('cols', 20)
        attrs.setdefault('rows', 1)
        super(ExtraThinTextarea, self).__init__(*args, **kwargs)
