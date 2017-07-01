# -*- coding: utf-8 -*-

import json

from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from ajax_select.fields import (
    AutoCompleteSelectMultipleField,
    AutoCompleteSelectMultipleWidget,
    make_plugin_options, pack_ids,
)
from ajax_select.registry import registry


class MigasAutoCompleteSelectMultipleWidget(AutoCompleteSelectMultipleWidget):
    """
    Class to override default AutoCompleteSelectMultipleWidget
    Incomprehensibly, it is not called get_objects in all cases to order values
    (since 1.5.0 version)
    """
    def render(self, name, value, attrs=None):
        if value is None:
            value = []

        final_attrs = self.build_attrs(self.attrs)
        final_attrs.update(attrs or {})
        final_attrs.pop('required', None)
        self.html_id = final_attrs.pop('id', name)

        lookup = registry.get(self.channel)

        objects = lookup.get_objects(value)  # always call to get_objects!!!

        current_ids = pack_ids([obj.pk for obj in objects])

        initial = [
            [lookup.format_item_display(obj), obj.pk]
            for obj in objects
        ]

        if self.show_help_text:
            help_text = self.help_text
        else:
            help_text = ''

        context = {
            'name': name,
            'html_id': self.html_id,
            'current': value,
            'current_ids': current_ids,
            'current_reprs': mark_safe(json.dumps(initial)),
            'help_text': help_text,
            'extra_attrs': mark_safe(flatatt(final_attrs)),
            'func_slug': self.html_id.replace("-", ""),
            'add_link': self.add_link,
        }
        context.update(make_plugin_options(lookup, self.channel, self.plugin_options, initial))
        templates = ('ajax_select/autocompleteselectmultiple_%s.html' % self.channel,
                     'ajax_select/autocompleteselectmultiple.html')
        out = render_to_string(templates, context)
        return mark_safe(out)


class MigasAutoCompleteSelectMultipleField(AutoCompleteSelectMultipleField):
    def __init__(self, channel, *args, **kwargs):
        self.channel = channel

        help_text = kwargs.get('help_text')
        show_help_text = kwargs.pop('show_help_text', False)
        widget_kwargs = {
            'channel': channel,
            'help_text': help_text,
            'show_help_text': show_help_text,
            'plugin_options': kwargs.pop('plugin_options', {})
        }
        widget_kwargs.update(kwargs.pop('widget_options', {}))
        kwargs['widget'] = MigasAutoCompleteSelectMultipleWidget(**widget_kwargs)
        kwargs['help_text'] = help_text

        super(MigasAutoCompleteSelectMultipleField, self).__init__(*args, **kwargs)
