# -*- coding: utf-8 -*-

import json

from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext as _

from migasfree.server.models import Deployment, Project, Store, Package
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
        percent = float(item['count']) / total * 100
        data.append({
            'name': u'{}'.format(dict(Application.CATEGORIES)[item['category']]),
            'value': item['count'],
            'y': float('{:.2f}'.format(percent)),
            'url': link.replace(
                '_REPLACE_',
                'category__exact={}'.format(item['category'])
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
        percent = float(item['count']) / total * 100
        data.append({
            'name': u'{}'.format(dict(Application.LEVELS)[item['level']]),
            'value': item['count'],
            'y': float('{:.2f}'.format(percent)),
            'url': link.replace(
                '_REPLACE_',
                'level__exact={}'.format(item['level'])
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
            count = sum(item['value'] for item in values[project.id])
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
        percent = float(item['count']) / total * 100
        data.append({
            'name': item['project__name'],
            'value': item['count'],
            'y': float('{:.2f}'.format(percent)),
            'url': link.replace(
                '_REPLACE_',
                'project__id__exact={}'.format(item['project__id'])
            ),
        })

    return {
        'title': _('Stores / Project'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('?_REPLACE_', ''),
    }


def deployment_by_enabled(user):
    total = Deployment.objects.scope(user).count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_deployment_changelist')
    )

    values_null = defaultdict(list)
    for item in Deployment.objects.scope(user).filter(
        enabled=True
    ).values(
        'project__id',
    ).annotate(
        count=Count('id')
    ).order_by('project__id', '-count'):
        percent = float(item.get('count')) / total * 100
        values_null[item.get('project__id')].append(
            {
                'name': _('Enabled'),
                'value': item.get('count'),
                'y': float('{:.2f}'.format(percent)),
                'url': link.replace(
                    '_REPLACE_',
                    'project__id__exact={}&enabled__exact=1'.format(
                        item.get('project__id')
                    )
                ),
            }
        )

    values_not_null = defaultdict(list)
    for item in Deployment.objects.scope(user).filter(
        enabled=False,
    ).values(
        'project__id',
    ).annotate(
        count=Count('id')
    ).order_by('project__id', '-count'):
        percent = float(item.get('count')) / total * 100
        values_not_null[item.get('project__id')].append(
            {
                'name': _('Disabled'),
                'value': item.get('count'),
                'y': float('{:.2f}'.format(percent)),
                'url': link.replace(
                    '_REPLACE_',
                    'project__id__exact={}&enabled__exact=0'.format(
                        item.get('project__id')
                    )
                ),
            }
        )

    data = []
    for project in Project.objects.scope(user).all():
        count = 0
        data_project = []
        if project.id in values_null:
            count += values_null[project.id][0]['value']
            data_project.append(values_null[project.id][0])
        if project.id in values_not_null:
            count += values_not_null[project.id][0]['value']
            data_project.append(values_not_null[project.id][0])
        if count:
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
                    'data': data_project
                }
            )

    return {
        'title': _('Deployments / Enabled'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('?_REPLACE_', ''),
    }


def deployment_by_schedule(user):
    total = Deployment.objects.scope(user).count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_deployment_changelist')
    )

    values_null = defaultdict(list)
    for item in Deployment.objects.scope(user).filter(
        schedule=None
    ).values(
        'project__id',
    ).annotate(
        count=Count('id')
    ).order_by('project__id', '-count'):
        percent = float(item.get('count')) / total * 100
        values_null[item.get('project__id')].append(
            {
                'name': _('Without schedule'),
                'value': item.get('count'),
                'y': float('{:.2f}'.format(percent)),
                'url': link.replace(
                    '_REPLACE_',
                    'project__id__exact={}&schedule__isnull=True'.format(
                        item.get('project__id')
                    )
                ),
            }
        )

    values_not_null = defaultdict(list)
    for item in Deployment.objects.scope(user).filter(
        ~Q(schedule=None)
    ).values(
        'project__id',
    ).annotate(
        count=Count('id')
    ).order_by('project__id', '-count'):
        percent = float(item.get('count')) / total * 100
        values_not_null[item.get('project__id')].append(
            {
                'name': _('With schedule'),
                'value': item.get('count'),
                'y': float('{:.2f}'.format(percent)),
                'url': link.replace(
                    '_REPLACE_',
                    'project__id__exact={}&schedule__isnull=False'.format(
                        item.get('project__id')
                    )
                ),
            }
        )

    data = []
    for project in Project.objects.scope(user).all():
        count = 0
        data_project = []
        if project.id in values_null:
            count += values_null[project.id][0]['value']
            data_project.append(values_null[project.id][0])
        if project.id in values_not_null:
            count += values_not_null[project.id][0]['value']
            data_project.append(values_not_null[project.id][0])
        if count:
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
                    'data': data_project
                }
            )

    return {
        'title': _('Deployments / Schedule'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('?_REPLACE_', ''),
    }


@login_required
def liberation_dashboard(request):
    user = request.user.userprofile

    return render(
        request,
        'software_dashboard.html',
        {
            'title': _("Summary"),
            'chart_options': {
                'no_data': _('There are no data to show'),
                'reset_zoom': _('Reset Zoom'),
                'months': json.dumps([
                    _('January'), _('February'), _('March'),
                    _('April'), _('May'), _('June'),
                    _('July'), _('August'), _('September'),
                    _('October'), _('November'), _('December')
                ]),
                'weekdays': json.dumps([
                    _('Sunday'), _('Monday'), _('Tuesday'), _('Wednesday'),
                    _('Thursday'), _('Friday'), _('Saturday')
                ]),
            },
            'deployment_by_enabled': deployment_by_enabled(user),
            'deployment_by_schedule': deployment_by_schedule(user),
            'store_by_project': store_by_project(user),
            'package_by_store': package_by_store(user),
            'application_by_category': application_by_category(),
            'application_by_level': application_by_level(),
        }
    )
