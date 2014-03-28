# -*- coding: utf-8 -*-

import json

from datetime import timedelta, datetime, date
from dateutil.relativedelta import *

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.db.models import Max, Count, Q

from migasfree.server.models import (
    Update,
    Platform,
    Computer,
    Schedule,
    ScheduleDelay,
    Login,
    UserProfile
)


def get_updates_time_range(
    begin_date, end_date, delta,
    compare_timeformat, xaxis_timeformat,
    by_platform=0
):
    data = []
    x_axis = []

    if by_platform == 0:
        updates = Update.objects.filter(
            date__gte=begin_date,
            date__lt=end_date
        ).values('date', 'computer').order_by('date')
    else:
        updates = Update.objects.filter(
            version__platform=by_platform
        ).filter(
            date__gte=begin_date,
            date__lt=end_date
        ).values('date', 'computer').order_by('date')

    step = 0
    if len(updates):
        next_date = updates[0]['date']
    else:
        next_date = begin_date
    distinct_computers = []
    count = 0
    for update in updates:
        if update['date'].strftime(compare_timeformat) == \
        next_date.strftime(compare_timeformat):
            if update['computer'] not in distinct_computers:
                count += 1
                distinct_computers.append(update['computer'])
        else:
            data.append([step, count])
            x_axis.append([step, next_date.strftime(xaxis_timeformat)])

            # reset counters
            step += 1
            next_date += delta
            distinct_computers = []
            if update['date'].strftime(compare_timeformat) == \
            next_date.strftime(compare_timeformat):
                count = 1
                distinct_computers.append(update['computer'])
            else:
                count = 0

    # append last value
    data.append([step, count])
    x_axis.append([step, next_date.strftime(xaxis_timeformat)])

    return {'data': data, 'x_axis': x_axis}


@login_required
def hourly_updated(request):
    title = _("Updated Computers / Hour")

    delta = timedelta(hours=1)
    end_date = datetime.now() + delta
    begin_date = end_date - timedelta(days=3)
    compare_timeformat = '%Y-%m-%d %H'
    xaxis_timeformat = "%H h. %b %d"

    updates_time_range = get_updates_time_range(
        begin_date, end_date, delta,
        compare_timeformat, xaxis_timeformat
    )

    if len(updates_time_range['data']) == 0:
        return render(
            request,
            'info.html',
            {
                'title': title,
                'contentpage': _('There are no updates')
            }
        )

    options = {
        'series': {
            'bars': {
                'show': True,
                'barWidth': 0.6,
                'align': 'center'
            }
        },
        'grid': {
            'hoverable': True
        },
        'legend': {
            'show': False,
        },
        'xaxis': {
            'tickLength': 5,
            'ticks': updates_time_range['x_axis'],
            'labelWidth': 80,
            'minTickSize': 4,
        },
    }

    return render(
        request,
        'lines.html',
        {
            "title": title,
            "options": json.dumps(options),
            "data": json.dumps([{
                'data': updates_time_range['data'],
                'label': _("Computers")
            }]),
        }
    )


@login_required
def daily_updated(request):
    title = _("Updated Computers / Day")

    delta = timedelta(days=1)
    end_date = date.today() + delta
    begin_date = end_date - timedelta(days=35)
    compare_timeformat = '%Y-%m-%d'
    xaxis_timeformat = "%b %d"

    updates_time_range = get_updates_time_range(
        begin_date, end_date, delta,
        compare_timeformat, xaxis_timeformat
    )

    if len(updates_time_range['data']) == 0:
        return render(
            request,
            'info.html',
            {
                'title': title,
                'contentpage': _('There are no updates')
            }
        )

    options = {
        'series': {
            'bars': {
                'show': True,
                'barWidth': 0.6,
                'align': 'center'
            }
        },
        'grid': {
            'hoverable': True
        },
        'legend': {
            'show': False,
        },
        'xaxis': {
            'tickLength': 5,
            'ticks': updates_time_range['x_axis'],
            'labelWidth': 80
        }
    }

    return render(
        request,
        'lines.html',
        {
            "title": title,
            "options": json.dumps(options),
            "data": json.dumps([{
                'data': updates_time_range['data'],
                'label': _("Computers")
            }]),
        }
    )


def month_year_iter(start_month, start_year, end_month, end_year):
    # http://stackoverflow.com/questions/5734438/how-to-create-a-month-iterator
    ym_start = 12 * start_year + start_month - 1
    ym_end = 12 * end_year + end_month - 1
    for ym in range(ym_start, ym_end):
        y, m = divmod(ym, 12)
        yield y, m + 1


# http://stackoverflow.com/questions/2170900/get-first-list-index-containing-sub-string-in-python
def index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
            return i
    return -1


@login_required
def monthly_updated(request):
    labels = {}
    data = {}
    new_data = {}
    x_axis = {}

    platforms = Platform.objects.only("id", "name")
    for platform in platforms:
        data[platform.id] = None
        new_data[platform.id] = []
        x_axis[platform.id] = None
        labels[platform.id] = platform.name

    total = []
    labels['total'] = _("Totals")

    delta = relativedelta(months=+1)
    end_date = date.today() + delta
    begin_date = end_date - relativedelta(months=+18)
    compare_timeformat = '%Y-%m'
    xaxis_timeformat = '%Y-%m'

    for platform in platforms:
        updates_time_range = get_updates_time_range(
            begin_date, end_date, delta,
            compare_timeformat, xaxis_timeformat,
            by_platform=platform.id
        )
        data[platform.id] = updates_time_range['data']
        x_axis[platform.id] = updates_time_range['x_axis']

    # shuffle data series
    i = 0
    x_axe = []
    for monthly in month_year_iter(
        begin_date.month, begin_date.year,
        end_date.month, end_date.year
    ):
        key = '%d-%02d' % (monthly[0], monthly[1])
        x_axe.append([i, key])
        total_month = 0
        for serie in data:
            index = index_containing_substring(x_axis[serie], key)
            if index >= 0:
                new_data[serie].append([i, data[serie][index][1]])
            else:
                new_data[serie].append([i, 0])

            total_month += new_data[serie][i][1]

        total.append([i, total_month])
        i += 1

    options = {
        'series': {
            'lines': {
                'show': True
            },
            'points': {
                'show': True
            }
        },
        'grid': {
            'hoverable': True
        },
        'legend': {
            'show': True,
            'position': 'nw'
        },
        'xaxis': {
            'tickLength': 5,
            'ticks': x_axe,
            'labelWidth': 80
        }
    }

    output_data = []
    for item in new_data:
        output_data.append({
            'data': new_data[item],
            'label': labels[item],
        })

    output_data.append({
        'data': total,
        'label': labels['total'],
    })

    return render(
        request,
        'lines.html',
        {
            "title": _("Updated Computers / Month"),
            "options": json.dumps(options),
            "data": json.dumps(output_data),
        }
    )


@login_required
def delay_schedule(request):
    title = _("Provided Computers / Delay")
    current_version = UserProfile.objects.get(id=request.user.id).version

    if current_version is None:
        return render(
            request,
            'info.html',
            {
                'title': title,
                'contentpage': _('Choose a version before continue')
            }
        )

     title += ' [%s]' % current_version.name

    data = []
    maximum_delay = 0
    for sched in Schedule.objects.all():
        lst_attributes = []
        d = 1
        value = 0
        line = []
        delays = ScheduleDelay.objects.filter(
            schedule__name=sched.name
        ).order_by("delay")
        for delay in delays:
            for i in range(d, delay.delay):
                line.append([i, value])

            for att in delay.attributes.all():
                lst_attributes.append(att.id)

            value = Login.objects.filter(
                Q(attributes__id__in=lst_attributes)
                & Q(computer__version=current_version.id)
            ).values('computer_id').annotate(lastdate=Max('date')).count()
            d = delay.delay

        line.append([d, value])

        maximum_delay = max(maximum_delay, d)
        data.append({
            'data': line,
            'label': sched.name,
        })

    if len(data) == 0:
        return render(
            request,
            'info.html',
            {
                'title': title,
                'contentpage': _('There are no defined schedules')
            }
        )

    x_axis = []
    for i in range(0, maximum_delay + 1):
        x_axis.append([i, _('%d days') % (i)])

    options = {
        'series': {
            'lines': {
                'show': True
            },
            'points': {
                'show': True
            }
        },
        'grid': {
            'hoverable': True
        },
        'legend': {
            'show': True,
            'position': 'se'
        },
        'xaxis': {
            'tickLength': 5,
            'ticks': x_axis,
            'labelWidth': 80,
            'minTickSize': 5
        }
    }

    return render(
        request,
        'lines.html',
        {
            "title": title,
            "options": json.dumps(options),
            "data": json.dumps(data),
        }
    )


@login_required
def version_computer(request):
    data = []
    total = 0
    for version in Computer.objects.values(
        "version__name",
        "version__id"
    ).annotate(
        count=Count("id")
    ):
        data.append(
            {
                "data": version.get("count"),
                "label": version.get("version__name"),
                'url': '%s?version__id__exact=%s' % (
                    reverse('admin:server_computer_changelist'),
                    version.get('version__id')
                )
            }
        )
        total += version.get("count")

    options = {
        'series': {
            'pie': {
                'show': True,
                'radius': 4.0 / 5,
                'label': {
                    'show': True,
                    'radius': 1,
                    'background': {
                        'opacity': 0.5,
                        'color': '#000'
                    }
                }
            }
        },
        'legend': {
            'show': True,
            'sorted': "ascending",
        },
        'grid': {
            'hoverable': True,
            'clickable': True,
        },
        'tooltip': True,
        'tooltipOpts': {
            'content': "%s (%y.0 / " + str(total) + ")"
        }
    }

    title = _("Computers / Version")

    if len(data) == 0:
        return render(
            request,
            'info.html',
            {
                'title': title,
                'contentpage': _('There are no computers')
            }
        )

    return render(
        request,
        'pie.html',
        {
            'title': title,
            'options': json.dumps(options),
            'data': json.dumps(data),
            'total': total,
            'formatter': 'labelFormatter',
            'labelFormatter': 'labelLegend',
        }
    )
