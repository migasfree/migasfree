# -*- coding: utf-8 -*-

import json

from collections import defaultdict
from datetime import timedelta, datetime

from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _

from migasfree.server.models import (
    Computer, Error, Fault,
    Platform, Project, Deployment,
    Migration, StatusLog,
    Synchronization
)

from . import HOURLY_RANGE
from .syncs import datetime_iterator


def productive_computers_by_platform(user):
    total = Computer.productive.scope(user).count()
    link = '{}?_REPLACE_&status__in={}'.format(
        reverse('admin:server_computer_changelist'),
        'intended,reserved,unknown'
    )

    values = defaultdict(list)
    for item in Computer.productive.scope(user).values(
        'project__name',
        'project__id',
        'project__platform__id'
    ).annotate(
        count=Count('id')
    ).order_by('project__platform__id', '-count'):
        percent = float(item.get('count')) / total * 100
        values[item.get('project__platform__id')].append(
            {
                'name': item.get('project__name'),
                'value': item.get('count'),
                'y': float('{:.2f}'.format(percent)),
                'url': link.replace(
                    '_REPLACE_',
                    'project__id__exact={}'.format(item.get('project__id'))
                ),
            }
        )

    data = []
    for platform in Platform.objects.scope(user).all():
        if platform.id in values:
            count = sum(item['value'] for item in values[platform.id])
            percent = float(count) / total * 100
            data.append(
                {
                    'name': platform.name,
                    'value': count,
                    'y': float('{:.2f}'.format(percent)),
                    'url': link.replace(
                        '_REPLACE_',
                        'project__platform__id__exact={}'.format(platform.id)
                    ),
                    'data': values[platform.id]
                }
            )

    return {
        'title': _('Productive Computers'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('_REPLACE_&', ''),
    }


def computers_by_machine(user):
    total = Computer.objects.scope(user).count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_computer_changelist')
    )

    values = defaultdict(list)
    data = []

    count_subscribed = Computer.subscribed.scope(user).count()
    count_subscribed_virtual = Computer.subscribed.scope(user).filter(machine='V').count()
    count_subscribed_physical = Computer.subscribed.scope(user).filter(machine='P').count()
    count_unsubscribed = Computer.unsubscribed.scope(user).count()
    count_unsubscribed_virtual = Computer.unsubscribed.scope(user).filter(machine='V').count()
    count_unsubscribed_physical = Computer.unsubscribed.scope(user).filter(machine='P').count()

    if count_subscribed:
        if count_subscribed_virtual:
            values['subscribed'].append(
                {
                    'name': _('Virtual'),
                    'value': count_subscribed_virtual,
                    'y': float('{:.2f}'.format(float(count_subscribed_virtual) / total * 100)),
                    'url': link.replace(
                        '_REPLACE_',
                        'status__in=intended,reserved,unknown,available,in repair&machine__exact=V'
                    )
                }
            )

        if count_subscribed_physical:
            values['subscribed'].append(
                {
                    'name': _('Physical'),
                    'value': count_subscribed_physical,
                    'y': float('{:.2f}'.format(float(count_subscribed_physical) / total * 100)),
                    'url': link.replace(
                        '_REPLACE_',
                        'status__in=intended,reserved,unknown,available,in repair&machine__exact=P'
                    )
                }
            )

        data.append(
            {
                'name': _('Subscribed'),
                'value': count_subscribed,
                'y': float('{:.2f}'.format(float(count_subscribed) / total * 100)),
                'url': link.replace(
                    '_REPLACE_',
                    'status__in=intended,reserved,unknown,available,in repair'
                ),
                'data': values['subscribed']
            },
        )

    if count_unsubscribed:
        if count_unsubscribed_virtual:
            values['unsubscribed'].append(
                {
                    'name': _('Virtual'),
                    'value': count_unsubscribed_virtual,
                    'y': float('{:.2f}'.format(float(count_unsubscribed_virtual) / total * 100)),
                    'url': link.replace(
                        '_REPLACE_',
                        'status__in=unsubscribed&machine__exact=V'
                    )
                }
            )

        if count_unsubscribed_physical:
            values['unsubscribed'].append(
                {
                    'name': _('Physical'),
                    'value': count_unsubscribed_physical,
                    'y': float('{:.2f}'.format(float(count_unsubscribed_physical) / total * 100)),
                    'url': link.replace(
                        '_REPLACE_',
                        'status__in=unsubscribed&machine__exact=P'
                    )
                }
            )

        data.append(
            {
                'name': _('Unsubscribed'),
                'value': count_unsubscribed,
                'y': float('{:.2f}'.format(float(count_unsubscribed) / total * 100)),
                'url': link.replace(
                    '_REPLACE_',
                    'status__in=unsubscribed'
                ),
                'data': values['unsubscribed']
            }
        )

    return {
        'title': _('Computers / Machine'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('?_REPLACE_', ''),
    }


def computers_by_status(user):
    total = Computer.objects.scope(user).exclude(status='unsubscribed').count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_computer_changelist')
    )

    values = dict()
    for item in Computer.objects.scope(user).exclude(
        status='unsubscribed'
    ).values(
        'status'
    ).annotate(
        count=Count('id')
    ).order_by('status', '-count'):
        status_name = _(dict(Computer.STATUS_CHOICES)[item.get('status')])
        percent = float(item.get('count')) / total * 100
        values[item.get('status')] = {
            'name': status_name,
            'value': item.get('count'),
            'y': float('{:.2f}'.format(percent)),
            'url': link.replace(
                '_REPLACE_',
                'status__in={}'.format(item.get('status'))
            ),
        }

    count_productive = values.get('intended', {}).get('value', 0) \
        + values.get('reserved', {}).get('value', 0) \
        + values.get('unknown', {}).get('value', 0)
    percent_productive = float(count_productive) / total * 100 if count_productive else 0
    data_productive = []
    if 'intended' in values:
        data_productive.append(values['intended'])
    if 'reserved' in values:
        data_productive.append(values['reserved'])
    if 'unknown' in values:
        data_productive.append(values['unknown'])

    count_unproductive = values.get('available', {}).get('value', 0) \
        + values.get('in repair', {}).get('value', 0)
    percent_unproductive = float(count_unproductive) / total * 100 if count_unproductive else 0
    data_unproductive = []
    if 'available' in values:
        data_unproductive.append(values['available'])
    if 'in repair' in values:
        data_unproductive.append(values['in repair'])

    data = [
        {
            'name': _('Productive'),
            'value': count_productive,
            'y': float('{:.2f}'.format(percent_productive)),
            'url': link.replace(
                '_REPLACE_',
                'status__in=intended,reserved,unknown'
            ),
            'data': data_productive,
        },
        {
            'name': _('Unproductive'),
            'value': count_unproductive,
            'y': float('{:.2f}'.format(percent_unproductive)),
            'url': link.replace(
                '_REPLACE_',
                'status__in=available,in repair'
            ),
            'data': data_unproductive,
        },
    ]

    return {
        'title': _('Subscribed Computers / Status'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('_REPLACE_', 'status__in=intended,reserved,unknown,available,in repair'),
    }


def unchecked_errors(user):
    total = Error.unchecked_count(user)
    link = '{}?checked__exact=0&_REPLACE_'.format(
        reverse('admin:server_error_changelist')
    )

    values = defaultdict(list)
    for item in Error.unchecked.scope(user).values(
        'project__platform__id',
        'project__id',
        'project__name',
    ).annotate(
        count=Count('id')
    ).order_by('project__id', '-count'):
        percent = float(item.get('count')) / total * 100
        values[item.get('project__platform__id')].append(
            {
                'name': item.get('project__name'),
                'value': item.get('count'),
                'y': float('{:.2f}'.format(percent)),
                'url': link.replace(
                    '_REPLACE_',
                    'project__id__exact={}'.format(
                        item.get('project__id')
                    )
                ),
            }
        )

    data = []
    for platform in Platform.objects.scope(user).all():
        if platform.id in values:
            count = sum(item['value'] for item in values[platform.id])
            percent = float(count) / total * 100
            data.append(
                {
                    'name': platform.name,
                    'value': count,
                    'y': float('{:.2f}'.format(percent)),
                    'url': link.replace(
                        '_REPLACE_',
                        'project__platform__id__exact={}'.format(platform.id)
                    ),
                    'data': values[platform.id]
                }
            )

    return {
        'title': _('Unchecked Errors'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('&_REPLACE_', ''),
    }


def unchecked_faults(user):
    total = Fault.unchecked_count()
    link = '{}?checked__exact=0&_REPLACE_'.format(
        reverse('admin:server_fault_changelist')
    )

    values = defaultdict(list)
    for item in Fault.unchecked.scope(user).values(
        'project__platform__id',
        'project__id',
        'project__name',
    ).annotate(
        count=Count('id')
    ).order_by('project__id', '-count'):
        percent = 0
        if total:
            percent = float(item.get('count')) / total * 100
        values[item.get('project__platform__id')].append(
            {
                'name': item.get('project__name'),
                'value': item.get('count'),
                'y': float('{:.2f}'.format(percent)),
                'url': link.replace(
                    '_REPLACE_',
                    'project__id__exact={}'.format(
                        item.get('project__id')
                    )
                ),
            }
        )

    data = []
    for platform in Platform.objects.scope(user).all():
        if platform.id in values:
            count = sum(item['value'] for item in values[platform.id])
            percent = 0
            if total:
                percent = float(count) / total * 100
            data.append(
                {
                    'name': platform.name,
                    'value': count,
                    'y': float('{:.2f}'.format(percent)),
                    'url': link.replace(
                        '_REPLACE_',
                        'project__platform__id__exact={}'.format(platform.id)
                    ),
                    'data': values[platform.id]
                }
            )

    return {
        'title': _('Unchecked Faults'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('&_REPLACE_', ''),
    }


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


@login_required
def stats_dashboard(request):
    now = timezone.now()
    end_date = datetime(now.year, now.month, now.day, now.hour) + timedelta(hours=1)
    begin_date = end_date - timedelta(days=HOURLY_RANGE)
    user = request.user.userprofile
    syncs = dict((i['hour'], i) for i in Synchronization.by_hour(begin_date, end_date, user))
    errors = dict((i['hour'], i) for i in Error.by_hour(begin_date, end_date, user))
    faults = dict((i['hour'], i) for i in Fault.by_hour(begin_date, end_date, user))
    migrations = dict((i['hour'], i) for i in Migration.by_hour(begin_date, end_date, user))
    status_logs = dict((i['hour'], i) for i in StatusLog.by_hour(begin_date, end_date, user))
    data_syncs = []
    data_errors = []
    data_faults = []
    data_migrations = []
    data_status = []

    for item in datetime_iterator(begin_date, end_date, delta=timedelta(hours=1)):
        data_syncs.append(syncs[item]['count'] if item in syncs else 0)
        data_errors.append(errors[item]['count'] if item in errors else 0)
        data_faults.append(faults[item]['count'] if item in faults else 0)
        data_migrations.append(migrations[item]['count'] if item in migrations else 0)
        data_status.append(status_logs[item]['count'] if item in status_logs else 0)

    return render(
        request,
        'stats_dashboard.html',
        {
            'title': _('Dashboard'),
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
            'productive_computers_by_platform': productive_computers_by_platform(user),
            'computers_by_machine': computers_by_machine(user),
            'computers_by_status': computers_by_status(user),
            'unchecked_errors': unchecked_errors(user),
            'unchecked_faults': unchecked_faults(user),
            'enabled_deployments': enabled_deployments(user),
            'last_day_events': {
                'title': _('History of events in the last %d hours') % (HOURLY_RANGE * 24),
                'start_date': {
                    'year': begin_date.year,
                    'month': begin_date.month - 1,  # JavaScript cast
                    'day': begin_date.day,
                    'hour': begin_date.hour,
                },
                'sync': {'name': _('Synchronizations'), 'data': json.dumps(data_syncs)},
                'error': {'name': _('Errors'), 'data': json.dumps(data_errors)},
                'fault': {'name': _('Faults'), 'data': json.dumps(data_faults)},
                'migration': {'name': _('Migrations'), 'data': json.dumps(data_migrations)},
                'status_log': {'name': _('Status Logs'), 'data': json.dumps(data_status)},
            },
        }
    )
