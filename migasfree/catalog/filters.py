# -*- coding: utf-8 -*-

import django_filters

from rest_framework import filters

from .models import Application, PackagesByProject


class ApplicationFilter(filters.FilterSet):
    description = django_filters.CharFilter(
        name='description', lookup_expr='icontains'
    )

    class Meta:
        model = Application
        fields = ['level', 'category', 'packages_by_project__project__name']


class PackagesByProjectFilter(filters.FilterSet):
    packages_to_install = django_filters.CharFilter(
        name='packages_to_install', lookup_expr='icontains'
    )

    class Meta:
        model = PackagesByProject
        fields = ['project__id', 'project__name']
