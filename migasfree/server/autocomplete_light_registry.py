# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from autocomplete_light import shortcuts as al

from .models import Computer


class ComputerAutocomplete(al.AutocompleteModelBase):
    search_fields = (settings.MIGASFREE_COMPUTER_SEARCH_FIELDS)
    model = Computer
    attrs = {
        'placeholder': _('Computer'),
        'data-autocomplete-minimum-characters': 1,
    }
    widget_attrs = {
        'data-widget-maximum-values': 1,
    }

    def __init__(self, request=None, values=None):
        super(ComputerAutocomplete, self).__init__(request, values)
        try:
            from django.db import connection
            table_names = connection.introspection.table_names()
            if 'server_computer' in table_names:
                self.choices = Computer.objects.all()
            else:
                self.choices = Computer.objects.none()
        except:
            self.choices = Computer.objects.none()

    def choice_label(self, choice):
        return choice.display()

al.register(ComputerAutocomplete)
