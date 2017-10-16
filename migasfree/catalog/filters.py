# -*- coding: utf-8 -*-

import django_filters

from .models import Application, PackagesByProject, Policy


class ApplicationFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(
        name='description', lookup_expr='icontains'
    )

    class Meta:
        model = Application
        fields = ['level', 'category', 'packages_by_project__project__name']


class PackagesByProjectFilter(django_filters.FilterSet):
    packages_to_install = django_filters.CharFilter(
        name='packages_to_install', lookup_expr='icontains'
    )

    class Meta:
        model = PackagesByProject
        fields = ['project__id', 'project__name']


class PolicyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        name='name', lookup_expr='icontains'
    )

    class Meta:
        model = Policy
        fields = ['name']
