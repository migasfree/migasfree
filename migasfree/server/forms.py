# -*- coding: utf-8 -*-

import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from dal import autocomplete

from .fields import MigasAutoCompleteSelectMultipleField
from .models import (
    Deployment, UserProfile, Computer, Device, DeviceLogical,
    Property, ServerAttribute, ServerProperty, Attribute,
    AttributeSet, Store, Package, FaultDefinition, DeviceModel,
)


class ParametersForm(forms.Form):
    id_query = forms.CharField(required=True, widget=forms.HiddenInput())
    user_project = forms.CharField(required=True, widget=forms.HiddenInput())


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
    included_attributes = MigasAutoCompleteSelectMultipleField(
        'attribute', required=False,
        label=_('included attributes'), show_help_text=False
    )
    excluded_attributes = MigasAutoCompleteSelectMultipleField(
        'attribute', required=False,
        label=_('excluded attributes'), show_help_text=False
    )
    available_packages = MigasAutoCompleteSelectMultipleField(
        'package', required=False,
        label=_('available packages'), show_help_text=False
    )

    def __init__(self, *args, **kwargs):
        super(DeploymentForm, self).__init__(*args, **kwargs)
        try:
            self.fields['start_date'].initial = datetime.date.today()
            self.fields['project'].initial = UserProfile.objects.get(
                pk=self.current_user.id
            ).project.id
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

        if 'project' not in cleaned_data:
            raise ValidationError(_('Project is required'))

        for pkg_id in cleaned_data.get('available_packages', []):
            pkg = Package.objects.get(pk=pkg_id)
            if pkg.project.id != cleaned_data['project'].id:
                raise ValidationError(
                    _('Package %s must belong to the project %s') % (
                        pkg, cleaned_data['project']
                    )
                )

        self._validate_active_computers(
            cleaned_data.get('included_attributes', [])
        )
        self._validate_active_computers(
            cleaned_data.get('excluded_attributes', [])
        )

    class Meta:
        model = Deployment
        fields = '__all__'


class StoreForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StoreForm, self).__init__(*args, **kwargs)
        try:
            self.fields['project'].initial = UserProfile.objects.get(
                pk=self.current_user.id
            ).project.id
            self.fields['project'].empty_label = None
        except (UserProfile.DoesNotExist, AttributeError):
            pass

    class Meta:
        model = Store
        fields = '__all__'


class PackageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PackageForm, self).__init__(*args, **kwargs)
        try:
            self.fields['project'].initial = UserProfile.objects.get(
                pk=self.current_user.id
            ).project.id
            self.fields['project'].empty_label = None
        except (UserProfile.DoesNotExist, AttributeError):
            pass

    class Meta:
        model = Package
        fields = '__all__'


class DeviceLogicalForm(forms.ModelForm):
    attributes = MigasAutoCompleteSelectMultipleField(
        'attribute', required=False,
        label=_('attributes')
    )

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

    class Meta:
        model = DeviceLogical
        fields = '__all__'


class PropertyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PropertyForm, self).__init__(*args, **kwargs)

        self.fields['code'].required = True

    class Meta:
        model = Property
        fields = '__all__'


class ServerAttributeForm(forms.ModelForm):
    computers = MigasAutoCompleteSelectMultipleField(
        'computer', required=False,
        label=_('Computers'), show_help_text=False
    )

    def __init__(self, *args, **kwargs):
        super(ServerAttributeForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['computers'].initial = \
                self.instance.tags.all()

        self.fields['property_att'].queryset = ServerProperty.objects.all()
        self.fields['property_att'].label = _('Tag Category')

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)
        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            instance.tags.clear()
            for computer_id in self.cleaned_data['computers']:
                instance.tags.add(computer_id)

        self.save_m2m = save_m2m
        if commit:
            instance.save()
            self.save_m2m()

        return instance

    class Meta:
        model = ServerAttribute
        fields = '__all__'


class ComputerForm(forms.ModelForm):
    tags = MigasAutoCompleteSelectMultipleField(
        'tag', required=False,
        label=_('tags'), show_help_text=False
    )

    class Meta:
        model = Computer
        fields = '__all__'


class AttributeSetForm(forms.ModelForm):
    included_attributes = MigasAutoCompleteSelectMultipleField(
        'attribute', required=False,
        label=_('included attributes'), show_help_text=False
    )
    excluded_attributes = MigasAutoCompleteSelectMultipleField(
        'attribute', required=False,
        label=_('excluded attributes'), show_help_text=False
    )

    class Meta:
        model = AttributeSet
        fields = '__all__'


class FaultDefinitionForm(forms.ModelForm):
    included_attributes = MigasAutoCompleteSelectMultipleField(
        'attribute', required=False,
        label=_('included attributes'), show_help_text=False
    )
    excluded_attributes = MigasAutoCompleteSelectMultipleField(
        'attribute', required=False,
        label=_('excluded attributes'), show_help_text=False
    )

    def __init__(self, *args, **kwargs):
        super(FaultDefinitionForm, self).__init__(*args, **kwargs)
        self.fields['users'].help_text = ''

    class Meta:
        model = FaultDefinition
        fields = '__all__'
        widgets = {
            'users': autocomplete.ModelSelect2Multiple(url='user_profile_autocomplete')
        }


class UserProfileForm(forms.ModelForm):
    user_permissions = MigasAutoCompleteSelectMultipleField(
        'permission', required=False,
        label=_('User Permissions'), show_help_text=False
    )

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['groups'].help_text = ''

    class Meta:
        model = UserProfile
        fields = (
            'username', 'first_name', 'last_name',
            'email', 'date_joined', 'last_login',
            'is_active', 'is_superuser', 'is_staff',
            'groups', 'user_permissions',
        )
        widgets = {
            'groups': autocomplete.ModelSelect2Multiple(url='group_autocomplete')
        }


class DeviceModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeviceModelForm, self).__init__(*args, **kwargs)
        self.fields['connections'].help_text = ''

    class Meta:
        model = DeviceModel
        fields = '__all__'
        widgets = {
            'connections': autocomplete.ModelSelect2Multiple(
                url='device_connection_autocomplete'
            )
        }


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = '__all__'
        widgets = {
            'model': autocomplete.ModelSelect2(url='device_model_autocomplete')
        }


class ExtraThinTextarea(forms.Textarea):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', {})
        attrs.setdefault('cols', 20)
        attrs.setdefault('rows', 1)
        super(ExtraThinTextarea, self).__init__(*args, **kwargs)
