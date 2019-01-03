# -*- coding: utf-8 -*-

import json

from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext as _

from migasfree.server.models import Project, Store, Package
from migasfree.catalog.models import Application


def application_by_category():
    total = Application.objects.count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:catalog_application_changelist')
    )

    data = []
    for item in Application.objects.values(
        'category',
    ).annotate(
        count=Count('category')
    ).order_by('-count'):
        percent = float(item.get('count')) / total * 100
        data.append({
            'name': u'{}'.format(dict(Application.CATEGORIES)[item.get('category')]),
            'value': item.get('count'),
            'y': float('{:.2f}'.format(percent)),
            'url': link.replace(
                '_REPLACE_',
                'category__exact={}'.format(item.get('category'))
            ),
        })

    return {
        'title': _('Applications / Category'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('?_REPLACE_', ''),
    }


def application_by_level():
    total = Application.objects.count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:catalog_application_changelist')
    )

    data = []
    for item in Application.objects.values(
        'level',
    ).annotate(
        count=Count('level')
    ).order_by('-count'):
        percent = float(item.get('count')) / total * 100
        data.append({
            'name': u'{}'.format(dict(Application.LEVELS)[item.get('level')]),
            'value': item.get('count'),
            'y': float('{:.2f}'.format(percent)),
            'url': link.replace(
                '_REPLACE_',
                'level__exact={}'.format(item.get('level'))
            ),
        })

    return {
        'title': _('Applications / Level'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('?_REPLACE_', ''),
    }


def package_by_store(user):
    total = Package.objects.scope(user).count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_package_changelist')
    )

    values = defaultdict(list)
    for item in Package.objects.scope(user).values(
        'project__id', 'store__id', 'store__name'
    ).annotate(
        count=Count('id')
    ).order_by('project__id', '-count'):
        percent = float(item.get('count')) / total * 100
        values[item.get('project__id')].append(
            {
                'name': item.get('store__name'),
                'value': item.get('count'),
                'y': float('{:.2f}'.format(percent)),
                'url': link.replace(
                    '_REPLACE_',
                    'project__id__exact={}&store__id__exact={}'.format(
                        item.get('project__id'),
                        item.get('store__id'),
                    )
                ),
            }
        )

    data = []
    for project in Project.objects.scope(user).all():
        if project.id in values:
            count = sum(item.get('value') for item in values[project.id])
            percent = float(count) / total * 100
            data.append(
                {
                    'name': project.name,
                    'value': count,
                    'y': float('{:.2f}'.format(percent)),
                    'url': link.replace(
                        '_REPLACE_',
                        'project__id__exact={}'.format(project.id)
                    ),
                    'data': values[project.id]
                }
            )

    return {
        'title': _('Packages / Store'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('?_REPLACE_', ''),
    }


def store_by_project(user):
    total = Store.objects.scope(user).count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_store_changelist')
    )

    data = []
    for item in Store.objects.scope(user).values(
        'project__name',
        'project__id',
    ).annotate(
        count=Count('id')
    ).order_by('-count'):
        percent = float(item.get('count')) / total * 100
        data.append({
            'name': item.get('project__name'),
            'value': item.get('count'),
            'y': float('{:.2f}'.format(percent)),
            'url': link.replace(
                '_REPLACE_',
                'project__id__exact={}'.format(item.get('project__id'))
            ),
        })

    return {
        'title': _('Stores / Project'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('?_REPLACE_', ''),
    }


@login_required
def stores_summary(request):
    user = request.user.userprofile

    return render(
        request,
        'stores_summary.html',
        {
            'title': _("Stores"),
            'chart_options': {
                'no_data': _('There are no data to show'),
                'reset_zoom': _('Reset Zoom'),
            },
            'store_by_project': store_by_project(user),
            'opts': Store._meta,
        }
    )


@login_required
def packages_summary(request):
    user = request.user.userprofile

    return render(
        request,
        'packages_summary.html',
        {
            'title': _("Packages/Sets"),
            'chart_options': {
                'no_data': _('There are no data to show'),
                'reset_zoom': _('Reset Zoom'),
            },
            'package_by_store': package_by_store(user),
            'opts': Package._meta,
        }
    )


@login_required
def applications_summary(request):
    return render(
        request,
        'applications_summary.html',
        {
            'title': _("Applications"),
            'chart_options': {
                'no_data': _('There are no data to show'),
                'reset_zoom': _('Reset Zoom'),
            },
            'application_by_category': application_by_category(),
            'application_by_level': application_by_level(),
            'opts': Application._meta,
        }
    )
