# -*- coding: utf-8 -*-

try:
    from django.conf.urls import patterns, include, url
except:
    from django.conf.urls.defaults import patterns, include, url

from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

from migasfree.server.views import *

urlpatterns = patterns('',
    url(r'^accounts/login/$', login, name='login'),

    url(
        r'^$',
        RedirectView.as_view(
            # cannot use reverse_lazy resolver with query string
            #url=reverse_lazy('admin:server_repository_changelist'),
            url='/admin/server/repository/?active__exact=1',
            query_string=True
        ),
        name='bootstrap'
    ),

    url(r'^alerts/$', alerts, name='alerts'),
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

    url(
        r'^chart/hourly_updated/$',
        hourly_updated,
        name='chart_hourly_updated'
    ),
    url(
        r'^chart/daily_updated/$',
        daily_updated,
        name='chart_daily_updated'
    ),
    url(
        r'^chart/monthly_updated/$',
        monthly_updated,
        name='chart_monthly_updated'
    ),
    url(
        r'^chart/delay_schedule/$',
        delay_schedule,
        name='chart_delay_schedule'
    ),
    url(
        r'^chart/version_computer/$',
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

    url(
        r'^connections_model/$',
        connections_model,
        name='connections_model'
    ),

    # backwards compatibility
    url(
        r'^migasfree/$',
        RedirectView.as_view(url=reverse_lazy('bootstrap')),
    ),
    url(
        r'^migasfree/main/$',
        RedirectView.as_view(url=reverse_lazy('bootstrap')),
    ),
    url(r'^status/$', RedirectView.as_view(url=reverse_lazy('bootstrap')),),
    url(r'^migasfree/api/$', api),  # for 2.x clients
)
