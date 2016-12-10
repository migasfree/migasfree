# -*- coding: UTF-8 -*-
import datetime

from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from ..functions import horizon, percent_horizon
from ..models.repository import Repository
from ..models.schedule_delay import ScheduleDelay

@login_required
def timeline(request):
    id = request.GET.get('id', 0)
    return HttpResponse(
        time_line(id)
    )

def time_line(id):

    repository = Repository.objects.get(pk=id)

    if repository.schedule is None or repository.schedule.id is None:
        return _('Without schedule')

    delays = ScheduleDelay.objects.filter(
        schedule__id=repository.schedule.id
    ).order_by('delay')

    if len(delays) == 0:
        return _('%s (without delays)') % repository.schedule

    date_format = "%Y-%m-%d"
    begin_date = datetime.datetime.strptime(
        str(horizon(repository.date, delays[0].delay)),
        date_format
    )
    end_date = datetime.datetime.strptime(
        str(horizon(
            repository.date,
            delays.reverse()[0].delay + delays.reverse()[0].duration
        )),
        date_format
    )

    timeline_delays = []
    for item in delays:
        hori = datetime.datetime.strptime(
            str(horizon(repository.date, item.delay)),
            date_format
        )
        horf = datetime.datetime.strptime(
            str(horizon(repository.date, item.delay + item.duration)),
            date_format
        )

        deploy = 'default'
        if hori <= datetime.datetime.now():
            deploy = 'success'

        timeline_delays.append({
            'deploy': deploy,
            'date': hori.strftime("%a-%b-%d"),
            'percent': int(percent_horizon(hori, horf)),
            'attributes': item.attributes.values_list("value", flat=True)
        })

    return render_to_string(
        'includes/deployment_timeline_detail.html',
        {
            'timeline': {
                'percent': int(percent_horizon(begin_date, end_date)),
                'schedule': repository.schedule,
                'delays': timeline_delays
            }
        }
    )

time_line.allow_tags = True
time_line.short_description = _('timeline')