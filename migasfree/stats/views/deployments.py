# -*- coding: utf-8 -*-

import json

from collections import defaultdict

from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext as _

from migasfree.server.models import Project, Deployment


def enabled_deployments(user):
    total = Deployment.objects.scope(user).filter(enabled=True).count()
    link = '{}?enabled__exact=1&_REPLACE_'.format(
        reverse('admin:server_deployment_changelist')
    )

    values_null = defaultdict(list)
    for item in Deployment.objects.scope(user).filter(
        enabled=True, schedule=None
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
        enabled=True,
    ).filter(
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
        'title': _('Enabled Deployments'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('&_REPLACE_', ''),
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
def deployments_summary(request):
    user = request.user.userprofile

    return render(
        request,
        'deployments_summary.html',
        {
            'title': _("Deployments"),
            'chart_options': {
                'no_data': _('There are no data to show'),
                'reset_zoom': _('Reset Zoom'),
            },
            'enabled_deployments': enabled_deployments(user),
            'deployment_by_enabled': deployment_by_enabled(user),
            'deployment_by_schedule': deployment_by_schedule(user),
            'opts': Deployment._meta,
        }
    )
