# -*- coding: utf-8 -*-

import os
import pygal
import json

from pygal.style import Style
from datetime import timedelta, datetime, date, time
from dateutil.relativedelta import relativedelta
from collections import defaultdict

from django.db.models import Max, Count, Q
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext as _

from ..models import (
    Synchronization,
    Platform,
    Computer,
    Schedule,
    ScheduleDelay,
    Project,
    Error,
    Fault,
    Deployment,
    Migration,
    StatusLog,
)
from ..utils import to_heatmap, to_timestamp

JS_FILE = 'file://' + os.path.join(
    settings.MIGASFREE_APP_DIR,
    'server',
    'static',
    'js',
    'pygal-tooltips.min.js'
)
BAR_STYLE = Style(
    font_family='Average Sans',
    background='transparent',
    colors=('#edc240',),
)
DEFAULT_STYLE = Style(
    font_family='Average Sans',
    background='transparent',
)
WIDTH = 800
HEIGHT = 400
LABEL_ROTATION = 45

HOURLY_RANGE = 3  # days
DAILY_RANGE = 35  # days
MONTHLY_RANGE = 18  # months


def get_syncs_time_range(start_date, end_date, platform=0, range_name='month'):
    syncs = Synchronization.objects.filter(
        created_at__range=(start_date, end_date)
    ).extra(
        {range_name: "date_trunc('" + range_name + "', created_at)"}
    ).values(range_name).annotate(
        count=Count("computer_id", distinct=True)
    ).order_by('-' + range_name)

    if platform:
        syncs = syncs.filter(project__platform=platform)

    return syncs


def datetime_iterator(from_date=None, to_date=None, delta=timedelta(minutes=1)):
    # from https://www.ianlewis.org/en/python-date-range-iterator
    from_date = from_date or datetime.now()
    while to_date is None or from_date <= to_date:
        yield from_date
        from_date = from_date + delta


@login_required
def synchronized_daily(request):
    delta = timedelta(days=1)
    end_date = date.today()
    begin_date = end_date - timedelta(days=DAILY_RANGE)
    range_name = 'day'

    updates_time_range = to_heatmap(
        get_syncs_time_range(
            begin_date, end_date + delta, range_name=range_name
        ),
        range_name
    )

    # filling the gaps (zeros)
    data = []
    labels = []
    for item in datetime_iterator(begin_date, end_date, delta):
        labels.append(item.strftime('%b %d'))
        index = str(to_timestamp(datetime.combine(item, time.min)))
        data.append(updates_time_range[index] if index in updates_time_range else 0)

    line_chart = pygal.Bar(
        no_data_text=_('There are no synchronizations'),
        show_legend=False,
        x_label_rotation=LABEL_ROTATION,
        style=BAR_STYLE,
        js=[JS_FILE],
        width=WIDTH,
        height=HEIGHT,
    )

    line_chart.x_labels = labels
    line_chart.add(_('Computers'), data)

    return render(
        request,
        'lines.html',
        {
            'title': _("Synchronized Computers / Day"),
            'chart': line_chart.render_data_uri(),
            'tabular_data': line_chart.render_table(),
        }
    )


def month_year_iter(start_month, start_year, end_month, end_year):
    # http://stackoverflow.com/questions/5734438/how-to-create-a-month-iterator
    ym_start = 12 * start_year + start_month - 1
    ym_end = 12 * end_year + end_month - 1
    for ym in range(ym_start, ym_end):
        y, m = divmod(ym, 12)
        yield y, m + 1


@login_required
def synchronized_monthly(request):
    line_chart = pygal.Line(
        no_data_text=_('There are no synchronizations'),
        x_label_rotation=LABEL_ROTATION,
        style=DEFAULT_STYLE,
        js=[JS_FILE],
        width=WIDTH,
        height=HEIGHT,
    )

    labels = {
        'total': _("Totals")
    }
    data = {}
    new_data = {}
    total = []
    range_name = 'month'

    delta = relativedelta(months=+1)
    end_date = date.today() + delta
    begin_date = end_date - relativedelta(months=+MONTHLY_RANGE)

    platforms = Platform.objects.only("id", "name")
    for platform in platforms:
        new_data[platform.id] = []
        labels[platform.id] = platform.name

        data[platform.id] = to_heatmap(
            get_syncs_time_range(
                begin_date, end_date, platform.id, range_name
            ),
            range_name
        )

    # shuffle data series
    x_axe = []
    for monthly in month_year_iter(
        begin_date.month, begin_date.year,
        end_date.month, end_date.year
    ):
        key = '%d-%02d' % (monthly[0], monthly[1])
        x_axe.append(key)
        total_month = 0
        for serie in data:
            index = str(to_timestamp(datetime(monthly[0], monthly[1], 1)))
            new_data[serie].append(data[serie][index] if index in data[serie] else 0)

            total_month += new_data[serie][-1]

        total.append(total_month)

    line_chart.x_labels = x_axe

    line_chart.add(labels['total'], total)
    for item in new_data:
        line_chart.add(labels[item], new_data[item])

    return render(
        request,
        'lines.html',
        {
            'title': _("Synchronized Computers / Month"),
            'chart': line_chart.render_data_uri(),
            'tabular_data': line_chart.render_table(),
        }
    )


@login_required
def delay_schedule(request, project_name=None):
    title = _("Provided Computers / Delay")
    project_selection = Project.get_project_names()

    if project_name is None:
        return render(
            request,
            'lines.html',
            {
                'title': title,
                'project_selection': project_selection,
            }
        )

    project = get_object_or_404(Project, name=project_name)
    title += ' [{}]'.format(project.name)

    line_chart = pygal.Line(
        no_data_text=_('There are no synchronizations'),
        x_label_rotation=LABEL_ROTATION,
        legend_at_bottom=True,
        style=DEFAULT_STYLE,
        js=[JS_FILE],
        width=WIDTH,
        height=HEIGHT,
    )

    maximum_delay = 0
    for schedule in Schedule.objects.all():
        lst_attributes = []
        d = 1
        value = 0
        line = []

        delays = ScheduleDelay.objects.filter(
            schedule__name=schedule.name
        ).order_by("delay")
        for delay in delays:
            for i in range(d, delay.delay):
                line.append([i, value])
                d += 1

            for duration in range(0, delay.duration):
                lst_att_delay = []
                for att in delay.attributes.all():
                    lst_att_delay.append(att.id)

                value += Computer.productive.extra(
                    select={'deployment': 'id'},
                    where=[
                        "computer_id %%%% %s = %s" %
                        (delay.duration, duration)
                    ]
                ).filter(
                    ~ Q(sync_attributes__id__in=lst_attributes) &
                    Q(sync_attributes__id__in=lst_att_delay) &
                    Q(project__id=project.id)
                ).values('id').annotate(lastdate=Max('sync_start_date')).count()

                line.append([d, value])

                d += 1

            for att in delay.attributes.all():
                lst_attributes.append(att.id)

        maximum_delay = max(maximum_delay, d)
        line_chart.add(schedule.name, [row[1] for row in line])

    labels = []
    for i in range(0, maximum_delay + 1):
        labels.append(_('%d days') % i)

    line_chart.x_labels = labels

    return render(
        request,
        'lines.html',
        {
            'title': title,
            'project_selection': project_selection,
            'current_project': project.name,
            'chart': line_chart.render_data_uri(),
            'tabular_data': line_chart.render_table(),
        }
    )


def productive_computers_by_platform(protocol, host):
    total = Computer.productive.count()
    link = '{}://{}{}?_REPLACE_&status__in={}'.format(
        protocol,
        host,
        reverse('admin:server_computer_changelist'),
        'intended,reserved,unknown'
    )

    values = defaultdict(list)
    for item in Computer.productive.values(
        "project__name",
        "project__id",
        "project__platform__id"
    ).annotate(
        count=Count("id")
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
    for platform in Platform.objects.all():
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
    }


def computers_by_machine(protocol, host):
    total = Computer.objects.count()
    link = '{}://{}{}?_REPLACE_'.format(
        protocol,
        host,
        reverse('admin:server_computer_changelist')
    )

    values = defaultdict(list)
    data = []

    count_subscribed = Computer.subscribed.count()
    count_subscribed_virtual = Computer.subscribed.filter(machine='V').count()
    count_subscribed_physical = Computer.subscribed.filter(machine='P').count()
    count_unsubscribed = Computer.unsubscribed.count()
    count_unsubscribed_virtual = Computer.unsubscribed.filter(machine='V').count()
    count_unsubscribed_physical = Computer.unsubscribed.filter(machine='P').count()

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
    }


def computers_by_status(protocol, host):
    total = Computer.objects.exclude(status='unsubscribed').count()
    link = '{}://{}{}?_REPLACE_'.format(
        protocol,
        host,
        reverse('admin:server_computer_changelist')
    )

    values = dict()
    for item in Computer.objects.exclude(
        status='unsubscribed'
    ).values(
        "status"
    ).annotate(
        count=Count("id")
    ).order_by('status', '-count'):
        status = _(dict(Computer.STATUS_CHOICES)[item.get('status')])
        percent = float(item.get('count')) / total * 100
        values[item.get('status')] = {
            'name': status,
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
    percent_productive = float(count_productive) / total * 100
    data_productive = []
    if 'intended' in values:
        data_productive.append(values['intended'])
    if 'reserved' in values:
        data_productive.append(values['reserved'])
    if 'unknown' in values:
        data_productive.append(values['unknown'])

    count_unproductive = values.get('available', {}).get('value', 0) \
        + values.get('in repair', {}).get('value', 0)
    percent_unproductive = float(count_unproductive) / total * 100
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
    }


def unchecked_errors(protocol, host):
    total = Error.unchecked_count()
    link = '{}://{}{}?checked__exact=0&_REPLACE_'.format(
        protocol,
        host,
        reverse('admin:server_error_changelist')
    )

    values = defaultdict(list)
    for item in Error.objects.filter(
        checked=False
    ).values(
        "computer__project__platform__id",
        "computer__project__id",
        "computer__project__name",
    ).annotate(
        count=Count("id")
    ).order_by('computer__project__id', '-count'):
        percent = float(item.get('count')) / total * 100
        values[item.get('computer__project__platform__id')].append(
            {
                'name': item.get('computer__project__name'),
                'value': item.get('count'),
                'y': float('{:.2f}'.format(percent)),
                'url': link.replace(
                    '_REPLACE_',
                    'project__id__exact={}'.format(
                        item.get('computer__project__id')
                    )
                ),
            }
        )

    data = []
    for platform in Platform.objects.all():
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
    }


def unchecked_faults(protocol, host):
    total = Fault.unchecked_count()
    link = '{}://{}{}?checked__exact=0&_REPLACE_'.format(
        protocol,
        host,
        reverse('admin:server_fault_changelist')
    )

    values = defaultdict(list)
    for item in Fault.objects.filter(
        checked=False
    ).values(
        "computer__project__platform__id",
        "computer__project__id",
        "computer__project__name",
    ).annotate(
        count=Count("id")
    ).order_by('computer__project__id', '-count'):
        percent = float(item.get('count')) / total * 100
        values[item.get('computer__project__platform__id')].append(
            {
                'name': item.get('computer__project__name'),
                'value': item.get('count'),
                'y': float('{:.2f}'.format(percent)),
                'url': link.replace(
                    '_REPLACE_',
                    'project__id__exact={}'.format(
                        item.get('computer__project__id')
                    )
                ),
            }
        )

    data = []
    for platform in Platform.objects.all():
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
        'title': _('Unchecked Faults'),
        'total': total,
        'data': json.dumps(data),
    }


def enabled_deployments(protocol, host):
    total = Deployment.objects.filter(enabled=True).count()
    link = '{}://{}{}?enabled__exact=1&_REPLACE_'.format(
        protocol,
        host,
        reverse('admin:server_deployment_changelist')
    )

    values_null = defaultdict(list)
    for item in Deployment.objects.filter(
        enabled=True, schedule=None
    ).values(
        "project__id",
    ).annotate(
        count=Count("id")
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
    for item in Deployment.objects.filter(
        enabled=True,
    ).filter(
        ~Q(schedule=None)
    ).values(
        "project__id",
    ).annotate(
        count=Count("id")
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
    for project in Project.objects.all():
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
    }


@login_required
def stats_dashboard(request):
    protocol = request.META.get('wsgi.url_scheme')
    host = request.META.get('HTTP_HOST')

    now = timezone.now()
    end_date = datetime(now.year, now.month, now.day, now.hour)
    begin_date = end_date - timedelta(days=HOURLY_RANGE)

    syncs = dict((i["hour"], i) for i in Synchronization.by_hour(begin_date, end_date))
    errors = dict((i["hour"], i) for i in Error.by_hour(begin_date, end_date))
    faults = dict((i["hour"], i) for i in Fault.by_hour(begin_date, end_date))
    migrations = dict((i["hour"], i) for i in Migration.by_hour(begin_date, end_date))
    status = dict((i["hour"], i) for i in StatusLog.by_hour(begin_date, end_date))
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
        data_status.append(status[item]['count'] if item in status else 0)

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
            'productive_computers_by_platform': productive_computers_by_platform(protocol, host),
            'computers_by_machine': computers_by_machine(protocol, host),
            'computers_by_status': computers_by_status(protocol, host),
            'unchecked_errors': unchecked_errors(protocol, host),
            'unchecked_faults': unchecked_faults(protocol, host),
            'enabled_deployments': enabled_deployments(protocol, host),
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
