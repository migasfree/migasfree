# -*- coding: utf-8 -*-

import pygal

from datetime import timedelta, datetime, date, time
from dateutil.relativedelta import relativedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from rest_framework import viewsets, status
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.test import APIClient

from migasfree.server.models import (
    Platform,
    Synchronization
)
from migasfree.server.utils import to_heatmap, to_timestamp

from . import (
    JS_FILE, MONTHLY_RANGE, DAILY_RANGE,
    LABEL_ROTATION, WIDTH, HEIGHT,
    DEFAULT_STYLE, BAR_STYLE
)


def get_syncs_time_range(start_date, end_date, platform=0, range_name='month', user=None):
    syncs = Synchronization.objects.scope(user).filter(
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
        from_date += delta


def month_year_iter(start_month, start_year, end_month, end_year):
    # http://stackoverflow.com/questions/5734438/how-to-create-a-month-iterator
    ym_start = 12 * start_year + start_month - 1
    ym_end = 12 * end_year + end_month - 1
    for ym in range(ym_start, ym_end):
        y, m = divmod(ym, 12)
        yield y, m + 1


class SyncStatsViewSet(viewsets.ViewSet):
    queryset = Synchronization.objects.all()

    def get_queryset(self):
        user = self.request.user.userprofile
        qs = self.queryset
        if not user.is_view_all():
            qs = qs.filter(computer_id__in=user.get_computers())
        return qs

    @list_route(methods=['get'])
    def monthly(self, request, format=None):
        fmt = '%Y%m'
        delta = relativedelta(months=+1)
        range_name = 'month'

        end = request.query_params.get('end', '')
        try:
            end = datetime.strptime(end, fmt)
        except ValueError:
            end = datetime.now() + delta

        begin = request.query_params.get('begin', '')
        try:
            begin = datetime.strptime(begin, fmt)
        except ValueError:
            begin = end - relativedelta(months=+MONTHLY_RANGE)

        platform_id = request.query_params.get('platform_id', None)
        if platform_id:
            get_object_or_404(Platform, pk=platform_id)

        user = request.user.userprofile
        updates_time_range = to_heatmap(
            get_syncs_time_range(
                begin, end, platform_id, range_name, user=user
            ),
            range_name
        )

        # shuffle data series
        data = []
        labels = []
        for monthly in month_year_iter(
            begin.month, begin.year,
            end.month, end.year
        ):
            key = '%d-%02d' % (monthly[0], monthly[1])
            labels.append(key)
            index = str(to_timestamp(datetime(monthly[0], monthly[1], 1)))
            data.append(updates_time_range[index] if index in updates_time_range else 0)

        return Response(zip(labels, data), status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def daily(self, request, format=None):
        now = datetime.now().timetuple()
        fmt = '%Y%m%d'
        delta = timedelta(days=1)
        range_name = 'day'

        end = request.query_params.get('end', '')
        try:
            end = datetime.strptime(end, fmt)
        except ValueError:
            end = datetime(now[0], now[1], now[2])

        begin = request.query_params.get('begin', '')
        try:
            begin = datetime.strptime(begin, fmt)
        except ValueError:
            begin = end - timedelta(days=DAILY_RANGE)

        user = request.user.userprofile
        updates_time_range = to_heatmap(
            get_syncs_time_range(
                begin, end + delta, range_name=range_name, user=user
            ),
            range_name
        )

        # filling the gaps (zeros)
        data = []
        labels = []
        for item in datetime_iterator(begin, end, delta):
            labels.append(item.strftime('%Y-%m-%d'))
            index = str(to_timestamp(datetime.combine(item, time.min)))
            data.append(updates_time_range[index] if index in updates_time_range else 0)

        return Response(zip(labels, data), status=status.HTTP_200_OK)


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
    x_labels = {}
    data = {}
    new_data = {}
    total = []

    delta = relativedelta(months=+1)
    end_date = date.today() + delta
    begin_date = end_date - relativedelta(months=+MONTHLY_RANGE)

    client = APIClient()
    client.force_authenticate(user=request.user)
    url = '/api/v1/token/stats/syncs/monthly/'

    platforms = Platform.objects.scope(request.user.userprofile).only("id", "name")
    for platform in platforms:
        new_data[platform.id] = []
        labels[platform.id] = platform.name

        response = client.get(
            '{}?platform_id={}'.format(url, platform.id),
            HTTP_ACCEPT_LANGUAGE=request.LANGUAGE_CODE
        )
        if hasattr(response, 'data') and response.status_code == status.HTTP_200_OK:
            x_labels[platform.id], data[platform.id] = zip(*response.data)

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
            new_data[serie].append(
                data[serie][x_labels[serie].index(key)] if key in x_labels[serie] else 0
            )
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
def synchronized_daily(request):
    line_chart = pygal.Bar(
        no_data_text=_('There are no synchronizations'),
        show_legend=False,
        x_label_rotation=LABEL_ROTATION,
        style=BAR_STYLE,
        js=[JS_FILE],
        width=WIDTH,
        height=HEIGHT,
    )
    data = []

    client = APIClient()
    client.force_authenticate(user=request.user)
    response = client.get(
        '/api/v1/token/stats/syncs/daily/',
        HTTP_ACCEPT_LANGUAGE=request.LANGUAGE_CODE
    )

    if hasattr(response, 'data') and response.status_code == status.HTTP_200_OK:
        labels, data = zip(*response.data)
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
