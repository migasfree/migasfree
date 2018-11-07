# -*- coding: utf-8 -*-

import json

from collections import defaultdict
from datetime import timedelta, datetime

from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _

from migasfree.server.models import (
    Error, Fault,
    Platform,
    Migration, StatusLog,
    Synchronization
)

from . import HOURLY_RANGE
from .syncs import datetime_iterator
from .computers import productive_computers_by_platform


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
    total = Fault.unchecked_count(user)
    link = '{}?checked__exact=0&user=me&_REPLACE_'.format(
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
            'unchecked_errors': unchecked_errors(user),
            'unchecked_faults': unchecked_faults(user),
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
