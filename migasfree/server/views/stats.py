# -*- coding: utf-8 -*-

from datetime import timedelta
from datetime import datetime
from datetime import date

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from django.db.models import Max
from django.db.models import Count
from django.db.models import Q

from migasfree.server.open_flash_chart import Chart
from migasfree.server.models import *


@login_required
def chart_selection(request):
    """
    Charts Menu of migasfree
    """

    return render(
        request,
        'chart_selection.html',
        {
            "title": _("Charts Menu"),
        }
    )


@login_required
def chart(request, chart_type):
    return render(
        request,
        'chart.html',
        {'ofc': reverse('chart_%s' % chart_type)}
    )


def hourly_updated(request):
    o_chart = Chart()
    timeformat = "%H h. %b %d "
    o_chart.title.text = _("Updated Computers / Hour")
    o_chart.title.style = "{font-size: 18px; color: #417690; text-align: center;}" # FIXME remove

    element1 = Chart()
    element1.values = []
    labels = []

    y = 24 * 4  # 4 days
    delta = timedelta(hours=1)
    n = datetime.now() - ((y - 25) * delta)
    n = datetime(n.year, n.month, n.day, 0)

    for i in range(y):
        value = Update.objects.filter(
            date__gte=n,
            date__lt=n + delta
        ).values('computer').distinct().count()

        element1.values.append(value)
        element1.tip = "#x_label#    #val# " + _("Computers")

        labels.append(n.strftime(timeformat))
        n += delta

    element1.type = "bar"
    # element1.dot_style.type = "dot"
    element1.width = 2
    element1.colour = "#417690"
    element1.text = ""  # Label
    element1.font_size = 10

    o_chart.x_axis.labels.stroke = 3
    o_chart.x_axis.labels.steps = 24
    o_chart.x_axis.labels.rotate = 270

    o_chart.x_axis.labels.labels = labels

    # y_axis
    o_chart.y_axis.max = max(element1.values)
    o_chart.y_axis.steps = 10 ** (len(str(o_chart.y_axis.max * 4)) - 2)
    o_chart.y_axis.max += o_chart.y_axis.steps / 2

    o_chart.elements = [element1, ]
    o_chart.y_legend.text = _("Computers")
    o_chart.y_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove
    o_chart.x_legend.text = _("Hour")
    o_chart.x_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove

    return HttpResponse(o_chart.create(), mimetype="text/plain")


def daily_updated(request):
    o_chart = Chart()
    timeformat = "%b %d"
    o_chart.title.text = _("Updated Computers / Day")
    o_chart.title.style = "{font-size: 18px; color: #417690; text-align: center;}" # FIXME remove

    element1 = Chart()
    element1.values = []
    labels = []

    days = 35
    delta = timedelta(days=1)
    n = date.today() - ((days - 1) * delta)
    for i in range(days):
        value = Update.objects.filter(
            date__gte=n,
            date__lt=n + delta
        ).values('computer').distinct().count()
        element1.values.append(value)
        element1.tip = "#x_label#    #val# " + _("Computers")
        labels.append(n.strftime(timeformat))
        n += delta

    element1.type = "bar"
    element1.dot_style.type = "dot"
    element1.width = 2
    element1.colour = "#417690"
    element1.text = ""  # Label
    element1.font_size = 10

    o_chart.x_axis.labels.rotate = 270
    o_chart.x_axis.labels.labels = labels

    # y_axis
    o_chart.y_axis.max = max(element1.values)
    o_chart.y_axis.steps = 10 ** (len(str(o_chart.y_axis.max * 4)) - 2)
    o_chart.y_axis.max += o_chart.y_axis.steps / 2

    o_chart.elements = [element1, ]

    o_chart.y_legend.text = _("Computers")
    o_chart.y_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove
    o_chart.x_legend.text = _("Day")
    o_chart.x_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove

    return HttpResponse(o_chart.create(), mimetype="text/plain")


def monthly_updated(request):
    o_chart = Chart()
    timeformat = "%b"
    o_chart.title.text = _("Updated Computers / Month")
    o_chart.title.style = "{font-size: 18px; color: #417690; text-align: center;}" # FIXME remove

    element1 = Chart()
    element1.values = []
    labels = []

    year = int(date.today().strftime("%Y"))
    years = [year - 2, year - 1, year]
    months = []
    for i in range(1, 13):
        months.append(date(year, i, 1).strftime(timeformat))

    for y in years:
        for m in range(1, 13):
            value = Update.objects.filter(
                date__month=m,
                date__year=y
            ).values('computer').distinct().count()
            element1.values.append(value)
            element1.tip = "#x_label#    #val# " + _("Computers")
            labels.append(str(months[m - 1]) + " " + str(y))

    element1.type = "bar"
    element1.dot_style.type = "dot"
    element1.width = 2
    element1.colour = "#417690"
    element1.text = ""  # Label
    element1.font_size = 10

    o_chart.x_axis.labels.rotate = 270
    o_chart.x_axis.labels.labels = labels

    # y_axis
    o_chart.y_axis.max = max(element1.values)
    o_chart.y_axis.steps = 10 ** (len(str(o_chart.y_axis.max * 4)) - 2)
    o_chart.y_axis.max += o_chart.y_axis.steps / 2

    o_chart.elements = [element1, ]

    o_chart.y_legend.text = _("Computers")
    o_chart.y_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove
    o_chart.x_legend.text = _("Month")
    o_chart.x_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove

    return HttpResponse(o_chart.create(), mimetype="text/plain")


def delay_schedule(request):
    o_chart = Chart()
    o_chart.title.text = _("Provided Computers / Delay")
    o_chart.title.style = "{font-size: 18px; color: #417690; text-align: center;}" # FIXME remove

    o_chart.elements = []
    o_schedules = Schedule.objects.all()
    # lines = []
    colours = [
        "#fa6900", "#417690", "#C4D318",
        "#FF00FF", "#00FFFF", "#50284A", "#7D7B6A",
    ]
    c = 0
    m = 0
    for sched in o_schedules:
        lst_attributes = []
        line = Chart()
        line.type = "line"
        line.dot_style.type = "dot"
        line.width = 2
        line.colour = colours[c]
        c += 1
        if c == len(colours):
            c = 0

        line.font_size = 10

        d = 1
        value = 0
        line.values = []
        delays = ScheduleDelay.objects.filter(
            schedule__name=sched.name
        ).order_by("delay")
        for delay in delays:
            for i in range(d, delay.delay):
                line.values.append(value)

            for att in delay.attributes.all():
                lst_attributes.append(att.id)

            value = Login.objects.filter(
                Q(attributes__id__in=lst_attributes)
            ).values('computer_id').annotate(lastdate=Max('date')).count()
            print lst_attributes  # DEBUG
            d = delay.delay
        line.values.append(value)
        line.text = sched.name
        line.tip = "#x_label# " + _("days") + " #val# " + _("Computers")

        m = max(m, max(line.values))
        o_chart.elements.append(line)

    o_chart.y_axis.max = m
    o_chart.y_axis.steps = 10 ** (len(str(o_chart.y_axis.max * 4)) - 2)
    o_chart.y_axis.max += o_chart.y_axis.steps / 2

    o_chart.y_legend.text = _("Computers")
    o_chart.y_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove
    o_chart.x_legend.text = _("Delay")
    o_chart.x_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove

    return HttpResponse(o_chart.create(), mimetype="text/plain")


def version_computer(request):
    o_chart = Chart()
    o_chart.title.text = _("Computers / Version")
    o_chart.title.style = "{font-size: 18px; color: #417690; text-align: center;}" # FIXME remove

    qry = Computer.objects.values("version__name").annotate(count=Count("id"))
    element1 = Chart()
    element1.type = "pie"
    element1.alpha = 0.6
    element1.start_angle = 35
    element1.animate = [{"type": "fade"}, {"type": "bounce", "distance": 10}]
    element1.tip = "#val# " + _("of") + " #total#<br>#percent#"
    element1.colours = ["#1C9E05", "#FF368D", "#417690", "#C4D318", "#50284A"]

    element1.gradient_fill = True
    element1.radius = 100
    element1.values = []
    for e in qry:
        """
        element1.values = [
            2000, 3000, 4000, {
                "value": 6000.511,
                "label": "hello (6000.51)",
                "on-click": "http://example.com"
            }
        ]
        """
        element1.values.append(
            {
                "value": e.get("count"),
                "label": e.get("version__name"),
            }
        )

    o_chart.num_decimals = 0
    o_chart.is_fixed_num_decimals_forced = True
    o_chart.is_decimal_separator_comma = False
    o_chart.is_thousand_separator_disabled = False

    # Add data to chart object
    o_chart.elements = [element1]

    return HttpResponse(o_chart.create(), mimetype="text/plain")
