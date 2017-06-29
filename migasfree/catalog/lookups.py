# -*- coding: utf-8 -*-

from django.utils.html import escape

from ajax_select import register, LookupChannel

from .models import Application


@register('application')
class ApplicationLookup(LookupChannel):
    model = Application

    def get_query(self, q, request):
        queryset = self.model.objects.filter(
            name__icontains=q
        ).order_by('name')

        return queryset

    def format_match(self, obj):
        return escape(obj.name)

    def format_item_display(self, obj):
        return obj.link()

    def can_add(self, user, other_model):
        return False

    def get_objects(self, ids):
        return self.model.objects.filter(pk__in=ids).order_by('name')
