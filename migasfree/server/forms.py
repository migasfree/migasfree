# -*- coding: utf-8 -*-

import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from dal import autocomplete
from ajax_select import make_ajax_form
from ajax_select.fields import AutoCompleteSelectMultipleField

from .models import (
    Deployment, UserProfile, Computer, Device, DeviceLogical,
    Property, ServerAttribute, ServerProperty, Attribute, Store, Package
)


class ParametersForm(forms.Form):
    id_query = forms.CharField(required=True, widget=forms.HiddenInput())
    user_version = forms.CharField(required=True, widget=forms.HiddenInput())


class DeviceReplacementForm(forms.Form):
    source = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        widget=autocomplete.ModelSelect2('device_autocomplete'),
        label=_('Source')
    )
    target = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        widget=autocomplete.ModelSelect2('device_autocomplete'),
        label=_('Target')
    )


class ComputerReplacementForm(forms.Form):
    source = forms.ModelChoiceField(
        queryset=Computer.objects.all(),
        widget=autocomplete.ModelSelect2('computer_autocomplete'),
        label=_('Source')
    )
    target = forms.ModelChoiceField(
        queryset=Computer.objects.all(),
        widget=autocomplete.ModelSelect2('computer_autocomplete'),
        label=_('Target')
    )


class AppendDevicesFromComputerForm(forms.Form):
    source = forms.ModelChoiceField(
        queryset=Computer.objects.all(),
        widget=autocomplete.ModelSelect2('computer_autocomplete'),
        label=_('Source')
    )
    target = forms.ModelMultipleChoiceField(
        queryset=Attribute.objects.all(),
        widget=autocomplete.ModelSelect2Multiple('attribute_autocomplete'),
        label=_('Target')
    )


class DeploymentForm(forms.ModelForm):
    included_attributes = AutoCompleteSelectMultipleField(
        'attribute', required=False
    )
    excluded_attributes = AutoCompleteSelectMultipleField(
        'attribute', required=False
    )
    available_packages = AutoCompleteSelectMultipleField(
        'package', required=False
    )

    class Meta:
        model = Deployment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DeploymentForm, self).__init__(*args, **kwargs)
        try:
            self.fields['start_date'].initial = datetime.date.today()
            self.fields['version'].initial = UserProfile.objects.get(
                pk=self.current_user.id
            ).version.id
        except (UserProfile.DoesNotExist, AttributeError):
            pass

    def _validate_active_computers(self, att_list):
        for att_id in att_list:
            attribute = Attribute.objects.get(pk=att_id)
            if attribute.property_att.prefix == 'CID':
                computer = Computer.objects.get(pk=int(attribute.value))
                if computer.status not in Computer.ACTIVE_STATUS:
                    raise ValidationError(
                        _('It is not possible to assign an inactive computer (%s) as an attribute')
                        % computer
                    )

    def clean(self):
        # http://stackoverflow.com/questions/7986510/django-manytomany-model-validation
        cleaned_data = super(DeploymentForm, self).clean()

        if 'version' not in cleaned_data:
            raise ValidationError(_('Version is required'))

        for pkg_id in cleaned_data.get('available_packages', []):
            pkg = Package.objects.get(pk=pkg_id)
            if pkg.version.id != cleaned_data['version'].id:
                raise ValidationError(
                    _('Package %s must belong to the version %s') % (
                        pkg, cleaned_data['version']
                    )
                )

        self._validate_active_computers(
            cleaned_data.get('included_attributes', [])
        )
        self._validate_active_computers(
            cleaned_data.get('excluded_attributes', [])
        )


class StoreForm(forms.ModelForm):

    class Meta:
        model = Store
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(StoreForm, self).__init__(*args, **kwargs)
        try:
            self.fields['version'].initial = UserProfile.objects.get(
                pk=self.current_user.id
            ).version.id
            self.fields['version'].empty_label = None
        except (UserProfile.DoesNotExist, AttributeError):
            pass


class PackageForm(forms.ModelForm):

    class Meta:
        model = Package
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PackageForm, self).__init__(*args, **kwargs)
        try:
            self.fields['version'].initial = UserProfile.objects.get(
                pk=self.current_user.id
            ).version.id
            self.fields['version'].empty_label = None
        except (UserProfile.DoesNotExist, AttributeError):
            pass


class DeviceLogicalForm(forms.ModelForm):
    attributes = AutoCompleteSelectMultipleField('attribute', required=False)

    class Meta:
        model = DeviceLogical
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DeviceLogicalForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['attributes'].initial = \
                self.instance.attributes.all().values_list('id', flat=True)

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)
        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            instance.attributes.clear()
            for attribute in self.cleaned_data['attributes']:
                instance.attributes.add(attribute)

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
        fields = '__all__'


class ServerAttributeForm(forms.ModelForm):
    x = make_ajax_form(Computer, {'tags': 'computer'})

    computers = x.declared_fields['tags']
    computers.label = _('Computers')

    class Meta:
        model = ServerAttribute
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ServerAttributeForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['computers'].initial = \
                self.instance.computer_set.all().values_list('id', flat=True)

        self.fields['property_att'].queryset = ServerProperty.objects.all()
        self.fields['property_att'].label = _('Tag Category')

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
    tags = AutoCompleteSelectMultipleField('tag', required=False)

    class Meta:
        model = Computer
        fields = '__all__'

    def clean(self):
        super(ComputerForm, self).clean()
        errors = []
        if self.cleaned_data.get('status') == 'available':
            if self.cleaned_data.get('tags'):
                errors.append(_("Status available can not have tags"))
            if self.cleaned_data.get('devices_logical'):
                errors.append(
                    _("Status available can not have devices logical")
                )

        if errors:
            raise forms.ValidationError(errors)

        return self.cleaned_data


class ExtraThinTextarea(forms.Textarea):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', {})
        attrs.setdefault('cols', 20)
        attrs.setdefault('rows', 1)
        super(ExtraThinTextarea, self).__init__(*args, **kwargs)
