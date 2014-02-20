# -*- coding: utf-8 -*-

import json

from datetime import timedelta, datetime, date

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import Max, Count, Q

from migasfree.server.models import *


@login_required
def hourly_updated(request):
    timeformat = "%H h. %b %d"

    data = []
    x_axis = []

    y = 24 * 2  # 4 days
    delta = timedelta(hours=1)
    n = datetime.now() - ((y - 25) * delta)
    n = datetime(n.year, n.month, n.day, 0)

    for i in range(y):
        value = Update.objects.filter(
            date__gte=n,
            date__lt=n + delta
        ).values('computer').distinct().count()

        # http://stackoverflow.com/questions/1077393/python-unix-time-doesnt-work-in-javascript
        #data.append([int(n.strftime("%s")) * 1000, value])

        data.append([i, value])
        x_axis.append([i, n.strftime(timeformat)])
        n += delta

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
            'ticks': x_axis,
            'labelWidth': 80,
            'minTickSize': 4,

            #'axisLabel': _("Hours"),

            #'mode': 'time',
            #'timeformat': timeformat,
            #'minTickSize': [5, 'hour'],
            #'monthNames': [
            #    _("Jan"), _("Feb"), _("Mar"), _("Apr"),
            #    _("May"), _("Jun"), _("Jul"), _("Aug"),
            #    _("Sep"), _("Oct"), _("Nov"), _("Dec")
            #]
        },
        #'yaxis': {
        #    'axisLabel': _("Computers"),
        #}
    }

    return render(
        request,
        'lines.html',
        {
            "title": _("Updated Computers / Hour"),
            "options": json.dumps(options),
            "data": json.dumps([{'data': data, 'label': _("Computers")}]),
        }
    )


@login_required
def daily_updated(request):
    timeformat = "%b %d"

    data = []
    x_axis = []

    days = 35
    delta = timedelta(days=1)
    n = date.today() - ((days - 1) * delta)
    for i in range(days):
        value = Update.objects.filter(
            date__gte=n,
            date__lt=n + delta
        ).values('computer').distinct().count()

        data.append([i, value])
        x_axis.append([i, n.strftime(timeformat)])
        n += delta

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
            'ticks': x_axis,
            'labelWidth': 80
        }
    }

    return render(
        request,
        'lines.html',
        {
            "title": _("Updated Computers / Day"),
            "options": json.dumps(options),
            "data": json.dumps([{'data': data, 'label': _("Computers")}]),
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
    platforms = Platform.objects.only("id", "name")

    labels = {}
    data = {}
    for platform in platforms:
        data[platform.id] = []
        labels[platform.id] = platform.name

    data['total'] = []
    labels['total'] = _("Totals")

    i = 0
    x_axis = []
    for monthly in month_year_iter(
        1,
        2012,
        int(date.today().strftime("%m")) + 1,
        int(date.today().strftime("%Y"))
    ):
        x_axis.append([i, '%d-%d' % (monthly[0], monthly[1])])
        total_monthly = 0
        for platform in platforms:
            value = Update.objects.filter(
                version__platform=platform.id
            ).filter(
                date__month=monthly[1],
                date__year=monthly[0]
            ).values('computer').distinct().count()

            data[platform.id].append([i, value])
            total_monthly += value

        data['total'].append([i, total_monthly])
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
        output_data.append({'data': data[item], 'label': labels[item]})

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
