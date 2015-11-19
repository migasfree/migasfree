# -*- coding: utf-8 -*-

import autocomplete_light.shortcuts as al

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

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

    def choice_label(self, choice):
        return choice.display()

al.register(ComputerAutocomplete)
