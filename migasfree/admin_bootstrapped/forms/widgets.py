"""
HTML5 input widgets.
TODO: Date widgets
"""
from django.forms.widgets import Input

class HTML5Input(Input):
    use_autofocus_fallback = False

    def render(self, *args, **kwargs):
        rendered_string = super(HTML5Input, self).render(*args, **kwargs)
        # js only works when an id is set
        if self.use_autofocus_fallback and kwargs.has_key('attrs') and kwargs['attrs'].get("id",False) and kwargs['attrs'].has_key("autofocus"):
            rendered_string += """<script>
if (!("autofocus" in document.createElement("input"))) {
  document.getElementById("%s").focus();
}
</script>""" % kwargs['attrs']['id']
        return rendered_string

class TextInput(HTML5Input):
    input_type = 'text'

    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control',
        }
        if attrs:
            default_attrs.update(attrs)
        super(TextInput, self).__init__(default_attrs)


class EmailInput(TextInput):
    input_type = 'email'

class TelephoneInput(TextInput):
    input_type = 'tel'

class URLInput(TextInput):
    input_type = 'url'

class SearchInput(TextInput):
    input_type = 'search'

class ColorInput(TextInput):
    """
    Not supported by any browsers at this time (Jan. 2010).
    """
    input_type = 'color'

class NumberInput(TextInput):
    input_type = 'number'

class RangeInput(TextInput):
    input_type = 'range'

class DateInput(TextInput):
    input_type = 'date'

class MonthInput(TextInput):
    input_type = 'month'

class WeekInput(TextInput):
    input_type = 'week'

class TimeInput(TextInput):
    input_type = 'time'

class DateTimeInput(TextInput):
    input_type = 'datetime'

class DateTimeLocalInput(TextInput):
    input_type = 'datetime-local'
