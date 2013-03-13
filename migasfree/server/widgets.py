from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class MigasfreeSplitDateTime(forms.SplitDateTimeWidget):
    """
    A SplitDateTime Widget that has some admin-specific styling.
    """
    def __init__(self, attrs=None):
        widgets = [AdminDateWidget, AdminTimeWidget]
        # Note that we're calling MultiWidget, not SplitDateTimeWidget, because
        # we want to define widgets.
        forms.MultiWidget.__init__(self, widgets, attrs)

    def format_output(self, rendered_widgets):
        return mark_safe(u'<p class="datetime">%s %s &emsp;&emsp; %s %s</p>' %
            ("", rendered_widgets[0], _('Time:'), rendered_widgets[1]))
        """
        return mark_safe(u'<p class="datetime">%s %s<br />%s %s</p>' % \
            (_('Date:'), rendered_widgets[0], _('Time:'), rendered_widgets[1]))
        """
