# -*- coding: utf-8 -*-

import json

from collections import defaultdict
from datetime import date
from dateutil.relativedelta import relativedelta

from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import ugettext as _

from ...server.models import (
    Synchronization, Migration, Platform, Project, StatusLog,
    Computer, Error, Fault, Notification,
)
from .syncs import month_year_iter
from . import MONTHLY_RANGE


def first_day_month(date_):
    return date(date_.year, date_.month, 1)


def month_interval():
    delta = relativedelta(months=+1)
    end_date = date.today() + delta
    begin_date = end_date - relativedelta(months=+MONTHLY_RANGE)

    return first_day_month(begin_date), end_date


def event_by_month(data, begin_date, end_date, model, field='project_id'):
    labels = {}
    new_data = {}
    chart_data = {}
    url = reverse('admin:server_{}_changelist'.format(model))

    if field == 'project_id':
        projects = Project.objects.only('id', 'name')
        for project in projects:
            new_data[project.id] = []
            labels[project.id] = project.name
    elif field == 'status':
        for status in Computer.STATUS_CHOICES:
            new_data[status[0]] = []
            labels[status[0]] = _(status[1])
    elif field == 'checked':
        new_data[True] = []
        new_data[False] = []
        labels[True] = _('Checked')
        labels[False] = _('Unchecked')

    # shuffle data series
    x_axe = []
    for monthly in month_year_iter(
        begin_date.month, begin_date.year,
        end_date.month, end_date.year
    ):
        start_date = date(monthly[0], monthly[1], 1)
        final_date = start_date + relativedelta(months=+1)
        querystring = {
            'created_at__gte': start_date.strftime('%Y-%m-%d'),
            'created_at__lt': final_date.strftime('%Y-%m-%d')
        }

        key = '%d-%02d' % (monthly[0], monthly[1])
        x_axe.append(key)
        value = list(filter(lambda item: item['year'] == monthly[0] and item['month'] == monthly[1], data))
        if field == 'project_id':
            for project in projects:
                if value:
                    count = list(filter(lambda item: item['project_id'] == project.id, value))
                    querystring['project__id__exact'] = project.id
                    new_data[project.id].append({
                        'y': count[0]['count'] if count else 0,
                        'url': '{}?{}'.format(url, urlencode(querystring))
                    })
                else:
                    new_data[project.id].append({
                        'y': 0,
                        'url': '#'
                    })
        elif field == 'status':
            for status in Computer.STATUS_CHOICES:
                if value:
                    count = list(filter(lambda item: item['status'] == status[0], value))
                    querystring['status__in'] = status[0]
                    new_data[status[0]].append({
                        'y': count[0]['count'] if count else 0,
                        'url': '{}?{}'.format(url, urlencode(querystring))
                    })
                else:
                    new_data[status[0]].append({
                        'y': 0,
                        'url': '#'
                    })
        elif field == 'checked':
            for val in [True, False]:
                if value:
                    count = list(filter(lambda item: item['checked'] == val, value))
                    querystring['checked__exact'] = 1 if val else 0
                    new_data[val].append({
                        'y': count[0]['count'] if count else 0,
                        'url': '{}?{}'.format(url, urlencode(querystring))
                    })
                else:
                    new_data[val].append({
                        'y': 0,
                        'url': '#'
                    })

    for item in new_data:
        chart_data[labels[item]] = new_data[item]

    return {'x_labels': x_axe, 'data': chart_data}


def sync_by_project(user):
    total = Synchronization.objects.scope(user).count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_synchronization_changelist')
    )

    data = []
    for item in Synchronization.objects.scope(user).values(
        'project__id', 'project__name'
    ).annotate(
        count=Count('project__id')
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
        'title': _('Synchronizations / Project'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('?_REPLACE_', ''),
    }


def sync_by_month(user):
    begin_date, end_date = month_interval()

    return event_by_month(
        Synchronization.stacked_by_month(user, begin_date),
        begin_date, end_date,
        'synchronization'
    )


@login_required
def syncs_summary(request):
    user = request.user.userprofile

    return render(
        request,
        'syncs_summary.html',
        {
            'title': _('Synchronizations'),
            'chart_options': {
                'no_data': _('There are no data to show'),
            },
            'sync_by_project': sync_by_project(user),
            'sync_by_month': sync_by_month(user),
            'opts': Synchronization._meta,
        }
    )


def migration_by_project(user):
    total = Migration.objects.scope(user).count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_migration_changelist')
    )

    values = defaultdict(list)
    for item in Migration.objects.scope(user).values(
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
        'title': _('Migrations / Project'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('?_REPLACE_', ''),
    }


def migration_by_month(user):
    begin_date, end_date = month_interval()

    return event_by_month(
        Migration.stacked_by_month(user, begin_date),
        begin_date, end_date,
        'migration'
    )


@login_required
def migrations_summary(request):
    user = request.user.userprofile

    return render(
        request,
        'migrations_summary.html',
        {
            'title': _('Migrations'),
            'chart_options': {
                'no_data': _('There are no data to show'),
            },
            'migration_by_project': migration_by_project(user),
            'migration_by_month': migration_by_month(user),
            'opts': Migration._meta,
        }
    )


def status_log_by_month(user):
    begin_date, end_date = month_interval()

    return event_by_month(
        StatusLog.stacked_by_month(user, begin_date, field='status'),
        begin_date,
        end_date,
        'statuslog',
        field='status'
    )


def status_log_by_status(user):
    total = StatusLog.objects.scope(user).count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_statuslog_changelist')
    )

    values = defaultdict(list)
    for item in StatusLog.objects.scope(user).values(
        'status',
    ).annotate(
        count=Count('id')
    ).order_by('status', '-count'):
        percent = float(item.get('count')) / total * 100
        values[item.get('status')].append(
            {
                'name': _(dict(Computer.STATUS_CHOICES)[item.get('status')]),
                'value': item.get('count'),
                'y': float('{:.2f}'.format(percent)),
                'url': link.replace(
                    '_REPLACE_',
                    'status__in={}'.format(item.get('status'))
                ),
            }
        )

    subscribed = 0
    subscribed += values['intended'][0]['value'] if 'intended' in values else 0
    subscribed += values['reserved'][0]['value'] if 'reserved' in values else 0
    subscribed += values['unknown'][0]['value'] if 'unknown' in values else 0
    subscribed += values['available'][0]['value'] if 'available' in values else 0
    subscribed += values['in repair'][0]['value'] if 'in repair' in values else 0
    unsubscribed = values['unsubscribed'][0]['value'] if 'unsubscribed' in values else 0
    data = [
        {
            'name': _('Subscribed'),
            'value': subscribed,
            'y': float('{:.2f}'.format(float(subscribed) / total * 100)) if subscribed else 0,
            'url': link.replace(
                '_REPLACE_',
                'status__in=intended,reserved,unknown,available,in repair'
            ),
            'data': values.get('intended', []) + values.get('reserved', [])
            + values.get('unknown', []) + values.get('available', []) + values.get('in repair', [])
        },
        {
            'name': _('unsubscribed'),
            'value': unsubscribed,
            'y': float('{:.2f}'.format(float(unsubscribed) / total * 100)) if unsubscribed else 0,
            'url': link.replace(
                '_REPLACE_',
                'status__in=unsubscribed'
            ),
            'data': values.get('unsubscribed', [])
        },
    ]

    return {
        'title': _('Status Logs / Status'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('?_REPLACE_', ''),
    }


@login_required
def status_logs_summary(request):
    user = request.user.userprofile

    return render(
        request,
        'status_logs_summary.html',
        {
            'title': _('Status Logs'),
            'chart_options': {
                'no_data': _('There are no data to show'),
            },
            'status_log_by_status': status_log_by_status(user),
            'status_log_by_month': status_log_by_month(user),
            'opts': StatusLog._meta,
        }
    )


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


def error_by_month(user):
    begin_date, end_date = month_interval()

    return event_by_month(
        Error.stacked_by_month(user, begin_date),
        begin_date,
        end_date,
        'error'
    )


def error_by_project(user):
    total = Error.objects.scope(user).count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_error_changelist')
    )

    values = defaultdict(list)
    for item in Error.objects.scope(user).values(
        'computer__status',
        'project__id',
        'project__name',
    ).annotate(
        count=Count('id')
    ).order_by('project__id', '-count'):
        percent = float(item.get('count')) / total * 100
        values[item.get('computer__status')].append(
            {
                'name': item.get('project__name'),
                'value': item.get('count'),
                'y': float('{:.2f}'.format(percent)),
                'url': link.replace(
                    '_REPLACE_',
                    'project__id__exact={}&computer__status__in={}'.format(
                        item.get('project__id'),
                        item.get('computer__status')
                    )
                ),
            }
        )

    data = []
    for status in Computer.STATUS_CHOICES:
        if status[0] in values:
            count = sum(item['value'] for item in values[status[0]])
            percent = float(count) / total * 100
            data.append(
                {
                    'name': _(status[1]),
                    'value': count,
                    'y': float('{:.2f}'.format(percent)),
                    'url': link.replace(
                        '_REPLACE_',
                        'computer__status__in={}'.format(status[0])
                    ),
                    'data': values[status[0]]
                }
            )

    return {
        'title': _('Errors / Project / Status'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('&_REPLACE_', ''),
    }


@login_required
def errors_summary(request):
    user = request.user.userprofile

    return render(
        request,
        'errors_summary.html',
        {
            'title': _('Errors'),
            'chart_options': {
                'no_data': _('There are no data to show'),
            },
            'unchecked_errors': unchecked_errors(user),
            'error_by_project': error_by_project(user),
            'error_by_month': error_by_month(user),
            'opts': Error._meta,
        }
    )


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


def fault_by_month(user):
    begin_date, end_date = month_interval()

    return event_by_month(
        Fault.stacked_by_month(user, begin_date),
        begin_date,
        end_date,
        'fault'
    )


def fault_by_definition(user):
    total = Fault.objects.scope(user).count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_fault_changelist')
    )

    data = []
    for item in Fault.objects.scope(user).values(
        'fault_definition__id', 'fault_definition__name'
    ).annotate(
        count=Count('fault_definition__id')
    ).order_by('-count'):
        percent = float(item.get('count')) / total * 100
        data.append({
            'name': item.get('fault_definition__name'),
            'value': item.get('count'),
            'y': float('{:.2f}'.format(percent)),
            'url': link.replace(
                '_REPLACE_',
                'Tag={}'.format(item.get('fault_definition__id'))
            ),
        })

    return {
        'title': _('Faults / Fault Definition'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('?_REPLACE_', ''),
    }


@login_required
def faults_summary(request):
    user = request.user.userprofile

    return render(
        request,
        'faults_summary.html',
        {
            'title': _('Faults'),
            'chart_options': {
                'no_data': _('There are no data to show'),
            },
            'unchecked_faults': unchecked_faults(user),
            'fault_by_definition': fault_by_definition(user),
            'fault_by_month': fault_by_month(user),
            'opts': Fault._meta,
        }
    )


def notification_by_month():
    begin_date, end_date = month_interval()

    return event_by_month(
        Notification.stacked_by_month(begin_date),
        begin_date,
        end_date,
        'notification',
        field='checked'
    )


@login_required
def notifications_summary(request):
    return render(
        request,
        'notifications_summary.html',
        {
            'title': _('Notifications'),
            'chart_options': {
                'no_data': _('There are no data to show'),
            },
            'notification_by_month': notification_by_month(),
            'opts': Notification._meta,
        }
    )
