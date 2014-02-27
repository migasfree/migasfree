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
    Login
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
    next_date = begin_date
    distinct_computers = []
    count = 0
    for update in updates:
        if update['date'].strftime(compare_timeformat) == next_date.strftime(compare_timeformat):
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
            if update['date'].strftime(compare_timeformat) == next_date.strftime(compare_timeformat):
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
    delta = timedelta(hours=1)
    end_date = datetime.now() + delta
    begin_date = end_date - timedelta(days=3)
    compare_timeformat = '%Y-%m-%d %H'
    xaxis_timeformat = "%H h. %b %d"

    updates_time_range = get_updates_time_range(
        begin_date, end_date, delta,
        compare_timeformat, xaxis_timeformat
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
            "title": _("Updated Computers / Hour"),
            "options": json.dumps(options),
            "data": json.dumps([{
                'data': updates_time_range['data'],
                'label': _("Computers")
            }]),
        }
    )

@login_required
def daily_updated(request):
    delta = timedelta(days=1)
    end_date = date.today() + delta
    begin_date = end_date - timedelta(days=35)
    compare_timeformat = '%Y-%m-%d'
    xaxis_timeformat = "%b %d"

    updates_time_range = get_updates_time_range(
        begin_date, end_date, delta,
        compare_timeformat, xaxis_timeformat
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
            "title": _("Updated Computers / Day"),
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


@login_required
def monthly_updated(request):
    labels = {}
    data = {}

    platforms = Platform.objects.only("id", "name")
    for platform in platforms:
        data[platform.id] = []
        labels[platform.id] = platform.name

    delta = relativedelta(months=+1)
    end_date = date.today() + delta
    begin_date = datetime(2012, 1, 1, 0, 0, 0)  #end_date - timedelta(years=2)
    compare_timeformat = '%Y-%m'
    xaxis_timeformat = '%Y-%m'

    total = []
    for platform in platforms:
        updates_time_range = get_updates_time_range(
            begin_date, end_date, delta,
            compare_timeformat, xaxis_timeformat,
            by_platform=platform.id
        )
        data[platform.id].append(updates_time_range['data'])

        for item in updates_time_range['data']:
            try:
                total[item[0]][1] += item[1]
            except:
                total.append([item[0], item[1]])

    i = 0
    x_axis = []
    for monthly in month_year_iter(
        1,
        2012,
        int(date.today().strftime("%m")) + 1,
        int(date.today().strftime("%Y"))
    ):
        x_axis.append([i, '%d-%d' % (monthly[0], monthly[1])])
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
            'ticks': x_axis,
            'labelWidth': 80
        }
    }

    output_data = []
    for item in data:
        output_data.append({'data': data[item][0], 'label': labels[item]})

    output_data.append({'data': total, 'label': _("Totals")})

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
            ).values('computer_id').annotate(lastdate=Max('date')).count()
            d = delay.delay

        line.append([d, value])

        maximum_delay = max(maximum_delay, d)
        data.append({
            'data': line,
            'label': sched.name,
        })

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
            "title": _("Provided Computers / Delay"),
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
                'radius': 4.0/5,
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
