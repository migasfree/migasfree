# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import (
    alerts, synchronized_daily, synchronized_monthly,
    project_schedule_delays, stats_dashboard,
    provided_computers_by_delay,
)

urlpatterns = [
    url(r'^alerts/$', alerts, name='alerts'),
    url(
        r'^stats/syncs/daily/$',
        synchronized_daily,
        name='stats_syncs_daily'
    ),
    url(
        r'^stats/syncs/monthly/$',
        synchronized_monthly,
        name='stats_syncs_monthly'
    ),
    url(
        r'^stats/schedule-delays/$',
        project_schedule_delays,
        name='stats_project_schedule_delays'
    ),
    url(
        r'^stats/schedule-delays/(?P<project_name>.+)/$',
        project_schedule_delays,
        name='stats_project_schedule_delays'
    ),
    url(
        r'^stats/dashboard/$',
        stats_dashboard,
        name='stats_dashboard'
    ),
    url(
        r'^stats/provided-computers-by-delay/$',
        provided_computers_by_delay,
        name='provided_computers',
    ),
]
