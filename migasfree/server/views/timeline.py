# -*- coding: UTF-8 -*-

import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from ..utils import time_horizon
from ..models import Deployment, ScheduleDelay


@login_required
def timeline(request):
    deploy = get_object_or_404(Deployment, pk=request.GET.get('id'))

    if deploy.schedule is None:
        return _('Without schedule')

    schedule_timeline = deploy.schedule_timeline()
    if not schedule_timeline:
        return _('%s (without delays)') % deploy.schedule

    delays = ScheduleDelay.objects.filter(
        schedule__id=deploy.schedule.id
    ).order_by('delay')

    timeline_delays = []
    date_format = "%Y-%m-%d"
    for item in delays:
        hori = datetime.datetime.strptime(
            str(time_horizon(deploy.start_date, item.delay)),
            date_format
        )
        horf = datetime.datetime.strptime(
            str(time_horizon(deploy.start_date, item.delay + item.duration)),
            date_format
        )

        result = 'default'
        if hori <= datetime.datetime.now():
            result = 'success'

        timeline_delays.append({
            'deploy': result,
            'date': hori,
            'percent': int(Deployment.get_percent(hori, horf)),
            'attributes': item.attributes.values_list("value", flat=True)
        })

    return render(
        request,
        'includes/deployment_timeline_detail.html',
        {
            'timeline': {
                'percent': schedule_timeline['percent'],
                'schedule': deploy.schedule,
                'delays': timeline_delays
            }
        }
    )

timeline.short_description = _('timeline')
