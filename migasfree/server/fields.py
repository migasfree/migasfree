# -*- coding: utf-8 -*-

from ajax_select.fields import (
    AutoCompleteSelectMultipleField,
    AutoCompleteSelectMultipleWidget,
)


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
        kwargs['widget'] = AutoCompleteSelectMultipleWidget(**widget_kwargs)
        kwargs['help_text'] = help_text

        super(AutoCompleteSelectMultipleField, self).__init__(*args, **kwargs)
