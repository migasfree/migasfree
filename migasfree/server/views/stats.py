# -*- coding: utf-8 -*-

import os
import pygal

from pygal.style import Style
from datetime import timedelta, datetime, date, time
from dateutil.relativedelta import *

from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models import Max, Count, Q

from ..models import (
    Synchronization,
    Platform,
    Computer,
    Schedule,
    ScheduleDelay,
    Version,
)
from ..functions import to_heatmap, to_timestamp

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
        syncs = syncs.filter(version__platform=platform)

    return syncs


def datetime_iterator(from_date=None, to_date=None, delta=timedelta(minutes=1)):
    # from https://www.ianlewis.org/en/python-date-range-iterator
    from_date = from_date or datetime.now()
    while to_date is None or from_date <= to_date:
        yield from_date
        from_date = from_date + delta


@login_required
def synchronized_hourly(request):
    delta = timedelta(hours=1)
    now = datetime.now()
    end_date = datetime(now.year, now.month, now.day, now.hour)
    begin_date = end_date - timedelta(days=HOURLY_RANGE)
    range_name = 'hour'

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
        labels.append(item.strftime('%H h. %b %d'))
        index = str(to_timestamp(item))
        data.append(updates_time_range[index] if index in updates_time_range else 0)

    line_chart = pygal.Bar(
        no_data_text=_('There are no updates'),
        show_legend=False,
        x_label_rotation=45,
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
            'title': _("Synchronized Computers / Hour"),
            'chart': line_chart.render_data_uri(),
            'tabular_data': line_chart.render_table(),
        }
    )


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
        no_data_text=_('There are no updates'),
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
        no_data_text=_('There are no updates'),
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
def delay_schedule(request, version_name=None):
    title = _("Provided Computers / Delay")
    version_selection = Version.get_version_names()

    if version_name is None:
        return render(
            request,
            'lines.html',
            {
                'title': title,
                'version_selection': version_selection,
            }
        )

    version = get_object_or_404(Version, name=version_name)
    title += ' [{}]'.format(version.name)

    line_chart = pygal.Line(
        no_data_text=_('There are no updates'),
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
                    Q(version=version.id)
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
            'version_selection': version_selection,
            'current_version': version.name,
            'chart': line_chart.render_data_uri(),
            'tabular_data': line_chart.render_table(),
        }
    )


@login_required
def version_computer(request):
    pie = pygal.Pie(
        no_data_text=_('There are no computers'),
        style=DEFAULT_STYLE,
        js=[JS_FILE],
        inner_radius=.4,
        width=WIDTH,
        height=HEIGHT,
    )
    total = Computer.productive.count()

    for version in Computer.productive.values(
        "version__name",
        "version__id"
    ).annotate(
        count=Count("id")
    ).order_by('version__platform__id', '-count'):
        percent = float(version.get('count')) / total * 100
        link = '%s://%s%s?version__id__exact=%s&status__in=%s' % (
            request.META.get('wsgi.url_scheme'),
            request.META.get('HTTP_HOST'),
            reverse('admin:server_computer_changelist'),
            version.get('version__id'),
            'intended,reserved,unknown'
        )

        pie.add(
            {
                'title': '{} ({})'.format(
                    version.get("version__name"),
                    version.get('count')
                ),
                'xlink': {
                    'href': link,
                    'target': '_top'
                }
            },
            [{
                'value': version.get("count"),
                'label': '{:.2f}%'.format(percent)
            }]
        )

    return render(
        request,
        'pie.html',
        {
            'title': _("Productive Computers / Version"),
            'total': total,
            'chart': pie.render_data_uri(),
        }
    )
