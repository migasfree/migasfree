# -*- coding: utf-8 -*-

from rest_framework import filters

from .models import Application


class ApplicationFilter(filters.FilterSet):
    class Meta:
        model = Application
        fields = ['level', 'category']
