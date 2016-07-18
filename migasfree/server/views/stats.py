# -*- coding: utf-8 -*-

import os
import pygal

from pygal.style import Style
from datetime import timedelta, datetime, date
from dateutil.relativedelta import *

from django.conf import settings
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
    UserProfile,
)

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

    if len(updates):
        next_date = updates[0]['date']
    else:
        next_date = begin_date

    distinct_computers = []
    step = 0
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
    delta = timedelta(hours=1)
    end_date = datetime.now() + delta
    begin_date = end_date - timedelta(days=3)

    updates_time_range = get_updates_time_range(
        begin_date, end_date, delta,
        compare_timeformat='%Y-%m-%d %H',
        xaxis_timeformat='%H h. %b %d'
    )

    line_chart = pygal.Bar(
        no_data_text=_('There are no updates'),
        show_legend=False,
        x_label_rotation=45,
        style=BAR_STYLE,
        js=[JS_FILE],
    )
    line_chart.x_labels = [row[1] for row in updates_time_range['x_axis']]
    line_chart.add(_('Computers'), [row[1] for row in updates_time_range['data']])

    return render(
        request,
        'lines.html',
        {
            'title': _("Updated Computers / Hour"),
            'chart': line_chart.render_data_uri(),
            'tabular_data': line_chart.render_table(),
        }
    )


@login_required
def daily_updated(request):
    delta = timedelta(days=1)
    end_date = date.today() + delta
    begin_date = end_date - timedelta(days=35)

    updates_time_range = get_updates_time_range(
        begin_date, end_date, delta,
        compare_timeformat='%Y-%m-%d',
        xaxis_timeformat='%b %d'
    )

    line_chart = pygal.Bar(
        no_data_text=_('There are no updates'),
        show_legend=False,
        x_label_rotation=45,
        style=BAR_STYLE,
        js=[JS_FILE],
    )
    line_chart.x_labels = [row[1] for row in updates_time_range['x_axis']]
    line_chart.add(_('Computers'), [row[1] for row in updates_time_range['data']])

    return render(
        request,
        'lines.html',
        {
            'title': _("Updated Computers / Day"),
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


# http://stackoverflow.com/questions/2170900/get-first-list-index-containing-sub-string-in-python
def index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
            return i

    return -1


@login_required
def monthly_updated(request):
    line_chart = pygal.Line(
        no_data_text=_('There are no updates'),
        x_label_rotation=45,
        style=DEFAULT_STYLE,
        js=[JS_FILE],
    )

    labels = {
        'total': _("Totals")
    }
    data = {}
    new_data = {}
    x_axis = {}
    total = []

    delta = relativedelta(months=+1)
    end_date = date.today() + delta
    begin_date = end_date - relativedelta(months=+18)

    platforms = Platform.objects.only("id", "name")
    for platform in platforms:
        new_data[platform.id] = []
        labels[platform.id] = platform.name

        updates_time_range = get_updates_time_range(
            begin_date, end_date, delta,
            compare_timeformat='%Y-%m',
            xaxis_timeformat='%Y-%m',
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

    line_chart.x_labels = [row[1] for row in x_axe]

    line_chart.add(labels['total'], [row[1] for row in total])
    for item in new_data:
        line_chart.add(labels[item], [row[1] for row in new_data[item]])

    return render(
        request,
        'lines.html',
        {
            'title': _("Updated Computers / Month"),
            'chart': line_chart.render_data_uri(),
            'tabular_data': line_chart.render_table(),
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

    line_chart = pygal.Line(
        no_data_text=_('There are no updates'),
        x_label_rotation=45,
        legend_at_bottom=True,
        style=DEFAULT_STYLE,
        js=[JS_FILE],
    )

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
                d += 1

            for duration in range(0, delay.duration):
                lst_att_delay = []
                for att in delay.attributes.all():
                    lst_att_delay.append(att.id)

                value += Login.objects.extra(
                    select={'deployment': 'computer_id'},
                    where=[
                        "computer_id %%%% %s = %s" %
                        (delay.duration, duration)
                    ]
                ).filter(
                    ~ Q(attributes__id__in=lst_attributes)
                    & Q(attributes__id__in=lst_att_delay)
                    & Q(computer__version=current_version.id)
                    & Q(computer__status__in=Computer.PRODUCTIVE_STATUS)
                ).values('computer_id').annotate(lastdate=Max('date')).count()

                line.append([d, value])

                d += 1

            for att in delay.attributes.all():
                lst_attributes.append(att.id)

        maximum_delay = max(maximum_delay, d)
        line_chart.add(sched.name, [row[1] for row in line])

    x_axis = []
    for i in range(0, maximum_delay + 1):
        x_axis.append([i, _('%d days') % i])

    line_chart.x_labels = [row[1] for row in x_axis]

    return render(
        request,
        'lines.html',
        {
            'title': title,
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
    )
    total = Computer.productives.count()

    for version in Computer.productives.values(
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
            'title': _("Productives Computers / Version"),
            'total': total,
            'chart': pie.render_data_uri(),
        }
    )
