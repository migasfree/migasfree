# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from django.views.generic import RedirectView

from migasfree.server.views import *

urlpatterns = patterns('',
    url(r'^accounts/login/$', login, name='login'),

    url(
        r'^$',
        RedirectView.as_view(url='/status/'),
        name='bootstrap'
    ),

    url(r'^ajax_status/$', ajax_status, name='ajax_status'),
    url(r'^status/$', status, name='dashboard'),
    url(r'^query/(?P<query_id>\d+)/$', query, name='query'),
    url(
        r'^computer_messages/$',
        computer_messages,
        name='computer_messages'
    ),
    url(
        r'^server_messages/$',
        server_messages,
        name="server_messages"
    ),

    url(r'^info/(.*)', info, name='package_info'),

    url(
        r'^change_version/$',
        change_version,
        name='change_version'
    ),

    url(r'^create_repos/$',
        create_repos,
        name='create_repos'
    ),

    url(r'^chart/(?P<chart_type>.*)/$', chart, name='chart_type'),
    url(
        r'^hourly_updated/$',
        hourly_updated,
        name='chart_hourly_updated'
    ),
    url(
        r'^daily_updated/$',
        daily_updated,
        name='chart_daily_updated'
    ),
    url(
        r'^monthly_updated/$',
        monthly_updated,
        name='chart_monthly_updated'
    ),
    url(
        r'^delay_schedule/$',
        delay_schedule,
        name='chart_delay_schedule'
    ),
    url(
        r'^version_computer/$',
        version_computer,
        name='chart_version_computer'
    ),

    url(
        r'^hardware/(.*)',
        hardware,
        name='hardware'
    ),
    url(
        r'^hardware_resume/(.*)',
        hardware_resume,
        name='hardware_resume'
    ),

    url(r'^api/$', api, name='api'),

    url(
        r'^get_versions/$',
        get_versions,
        name='get_versions'
    ),
    url(
        r'^get_computer_info/$',
        get_computer_info,
        name='get_computer_info'
    ),
    url(
        r'^computer_label/$',
        computer_label,
        name='computer_label'
    ),


    (r'^device/(.*)', device),
    # (r'^get_device/(.*)', get_device),

    # backwards compatibility
    url(
        r'^migasfree/$',
        RedirectView.as_view(url='/status/'),
    ),
    url(
        r'^migasfree/main/$',
        RedirectView.as_view(url='/status/'),
    ),
    url(r'^migasfree/api/$', api),  # for 2.x clients
)
