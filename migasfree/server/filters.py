# -*- coding: utf-8 -*-

from django.contrib.admin.filters import ChoicesFieldListFilter
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django.utils.translation import ugettext as _

from migasfree.middleware import threadlocals
from .models import ClientProperty, TagType


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
            'selected': self.lookup_val == 'intended,reserved,unknown,available,in repair',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'intended,reserved,unknown,available,in repair'}
            ),
            'display': _("Subscribed")
        }

        yield {
            'selected': self.lookup_val == 'intended,reserved,unknown',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'intended,reserved,unknown'}
            ),
            'display': "* " + _("Productive")
        }

        yield {
            'selected': self.lookup_val == 'intended',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'intended'}
            ),
            'display': "--- " + _("intended")
        }

        yield {
            'selected': self.lookup_val == 'reserved',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'reserved'}
            ),
            'display': "--- " + _("reserved")
        }

        yield {
            'selected': self.lookup_val == 'unknown',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'unknown'}
            ),
            'display': "--- " + _("unknown")
        }

        yield {
            'selected': self.lookup_val == 'available,in repair',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'available,in repair'}
            ),
            'display': "* " + _("Unproductive")
        }

        yield {
            'selected': self.lookup_val == 'in repair',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'in repair'}
            ),
            'display': "--- " + _("in repair")
        }

        yield {
            'selected': self.lookup_val == 'available',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'available'}
            ),
            'display': "--- " + _("available")
        }

        yield {
            'selected': self.lookup_val == 'unsubscribed',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'unsubscribed'}
            ),
            'display': _("unsubscribed")
        }


class TagFilter(SimpleListFilter):
    title = _('Tag Type')
    parameter_name = 'Tag'

    def lookups(self, request, model_admin):
        return [(c.id, c.name) for c in TagType.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(property_att__id__exact=self.value())
        else:
            return queryset


class FeatureFilter(SimpleListFilter):
    title = _('Property')
    parameter_name = 'Attribute'

    def lookups(self, request, model_admin):
        return [(c.id, c.name) for c in ClientProperty.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(property_att__id__exact=self.value())
        else:
            return queryset


class UserFaultFilter(SimpleListFilter):
    title = _('User')
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        return (
            ('me', _('To check for me')),
            ('only_me', _('Assigned to me')),
            ('others', _('Assigned to others')),
            ('no_assign', _('Not assigned')),
        )

    def queryset(self, request, queryset):
        lst = [threadlocals.get_current_user().id]
        if self.value() == 'me':
            return queryset.filter(
                Q(faultdef__users__id__in=lst) | Q(faultdef__users=None)
            )
        elif self.value() == 'only_me':
            return queryset.filter(Q(faultdef__users__id__in=lst))
        elif self.value() == 'others':
            return queryset.exclude(
                faultdef__users__id__in=lst
            ).exclude(faultdef__users=None)
        elif self.value() == 'no_assign':
            return queryset.filter(Q(faultdef__users=None))
