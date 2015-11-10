# -*- coding: utf-8 -*-

from django.contrib.admin.filters import ChoicesFieldListFilter
from .functions import trans as _


class ProductiveFilterSpec(ChoicesFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super(ProductiveFilterSpec, self).__init__(field, request, params,
            model, model_admin, field_path)
        self.lookup_kwarg = '%s__in' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg)
        self.title = _('Status')

    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
            'display': _('All')
        }

        yield {
            'selected': self.lookup_val == 'intended,reserved,unknown',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'intended,reserved,unknown'}
            ),
            'display': _("Productive")
        }

        yield {
            'selected': self.lookup_val == 'intended',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'intended'}
            ),
            'display': "* " + _("intended")
        }

        yield {
            'selected': self.lookup_val == 'reserved',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'reserved'}
            ),
            'display': "* " + _("reserved")
        }

        yield {
            'selected': self.lookup_val == 'unknown',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'unknown'}
            ),
            'display': "* " + _("unknown")
        }

        yield {
            'selected': self.lookup_val == 'available,unsubscribed,in repair',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'available,unsubscribed,in repair'}
            ),
            'display': _("Unproductive")
        }

        yield {
            'selected': self.lookup_val == 'in repair',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'in repair'}
            ),
            'display': "* " + _("in repair")
        }

        yield {
            'selected': self.lookup_val == 'available',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'available'}
            ),
            'display': "* " + _("available")
        }

        yield {
            'selected': self.lookup_val == 'unsubscribed',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'unsubscribed'}
            ),
            'display': "* " + _("unsubscribed")
        }

