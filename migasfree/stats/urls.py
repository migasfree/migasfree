# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import (
    alerts, synchronized_daily, synchronized_monthly,
    project_schedule_delays, stats_dashboard,
    provided_computers_by_delay, devices_summary,
    computers_summary, stores_summary,
    packages_summary, applications_summary,
    deployments_summary,
    device_models_summary,
    attributes_summary, tags_summary,
    syncs_summary, migrations_summary,
    status_logs_summary, faults_summary,
    errors_summary, notifications_summary,
    event_history,
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
        r'^stats/event-history/$',
        event_history,
        name='event_history'
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
    url(
        r'^devices/$',
        devices_summary,
        name='devices_summary'
    ),
    url(
        r'^stores/$',
        stores_summary,
        name='stores_summary'
    ),
    url(
        r'^packages/$',
        packages_summary,
        name='packages_summary'
    ),
    url(
        r'^applications/$',
        applications_summary,
        name='applications_summary'
    ),
    url(
        r'^computers/$',
        computers_summary,
        name='computers_summary'
    ),
    url(
        r'^deployments/$',
        deployments_summary,
        name='deployments_summary'
    ),
    url(
        r'^devicemodels/$',
        device_models_summary,
        name='device_models_summary'
    ),
    url(
        r'^attributes/$',
        attributes_summary,
        name='attributes_summary'
    ),
    url(
        r'^tags/$',
        tags_summary,
        name='tags_summary'
    ),
    url(
        r'^synchronizations/$',
        syncs_summary,
        name='syncs_summary'
    ),
    url(
        r'^migrations/$',
        migrations_summary,
        name='migrations_summary'
    ),
    url(
        r'^statuslogs/$',
        status_logs_summary,
        name='status_logs_summary'
    ),
    url(
        r'^faults/$',
        faults_summary,
        name='faults_summary'
    ),
    url(
        r'^errors/$',
        errors_summary,
        name='errors_summary'
    ),
    url(
        r'^notifications/$',
        notifications_summary,
        name='notifications_summary'
    ),
]
