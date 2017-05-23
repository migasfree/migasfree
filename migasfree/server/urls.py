# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import RedirectView, TemplateView
from django.core.urlresolvers import reverse_lazy
from django.conf import settings

from .views import *

urlpatterns = [
    url(r'^accounts/login/$', login, name='login'),

    url(
        r'^$',
        TemplateView.as_view(template_name='welcome.html'),
        name='bootstrap'
    ),

    url(
        r'^favicon\.ico$',
        RedirectView.as_view(
            url='%simg/favicon.png' % settings.STATIC_URL
        ),
    ),

    url(r'^alerts/$', alerts, name='alerts'),
    url(r'^query/(?P<query_id>\d+)/$', get_query, name='query'),
    url(
        r'^computer_messages/$',
        computer_messages,
        name='computer_messages'
    ),

    url(r'^info/(.*)', info, name='package_info'),

    url(
        r'^chart/synchronized_daily/$',
        synchronized_daily,
        name='chart_synchronized_daily'
    ),
    url(
        r'^chart/synchronized_monthly/$',
        synchronized_monthly,
        name='chart_synchronized_monthly'
    ),
    url(
        r'^chart/delay_schedule/$',
        delay_schedule,
        name='chart_delay_schedule'
    ),
    url(
        r'^chart/delay_schedule/(?P<project_name>.+)/$',
        delay_schedule,
        name='chart_delay_schedule'
    ),
    url(
        r'^chart/dashboard/$',
        stats_dashboard,
        name='stats_dashboard'
    ),

    url(
        r'^hardware_resume/(.*)',
        hardware_resume,
        name='hardware_resume'
    ),
    url(
        r'^hardware_extract/(.*)',
        hardware_extract,
        name='hardware_extract'
    ),

    url(
        r'^admin/server/computer/change_status/$',
        computer_change_status,
        name='computer_change_status'
    ),

    url(
        r'^admin/server/computer/delete_selected/$',
        computer_delete_selected,
        name='computer_delete_selected'
    ),

    url(
        r'^admin/server/computer/(?P<pk>\d+)/delete/$',
        ComputerDelete.as_view(),
        name='computer_delete'
    ),

    url(
        r'^admin/server/platform/delete_selected/$',
        platform_delete_selected,
        name='platform_delete_selected'
    ),

    url(
        r'^admin/server/platform/(?P<pk>\d+)/delete/$',
        PlatformDelete.as_view(),
        name='platform_delete'
    ),

    url(
        r'^admin/server/project/(?P<pk>\d+)/delete/$',
        ProjectDelete.as_view(),
        name='project_delete'
    ),

    url(
        r'^admin/preferences/$',
        preferences,
        name='preferences'
    ),

    url(r'^api/$', api, name='api'),

    url(
        r'^get_projects/$',
        get_projects,
        name='get_projects'
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
        r'^get_key_repositories/$',
        get_key_repositories,
        name='get_key_repositories'
    ),
    url(
        r'^timeline/$',
        timeline,
        name='timeline',
    ),
    url(
        r'^connections_model/$',
        connections_model,
        name='connections_model'
    ),

    url(
        r'^computer_replacement/$',
        computer_replacement,
        name='computer_replacement'
    ),

    url(
        r'^computer/(?P<pk>\d+)/events/$',
        computer_events,
        name='computer_events',
    ),

    url(
        r'^computer/(?P<pk>\d+)/simulate/$',
        computer_simulate_sync,
        name='computer_simulate_sync',
    ),

    url(
        r'^link/$',
        link,
        name='link',
    ),

    url(
        r'^device_replacement/$',
        device_replacement,
        name='device_replacement'
    ),

    url(
        r'^computer_autocomplete/$',
        ComputerAutocomplete.as_view(),
        name='computer_autocomplete',
    ),

    url(
        r'^attribute_autocomplete/$',
        AttributeAutocomplete.as_view(),
        name='attribute_autocomplete',
    ),

    url(
        r'^device_autocomplete/$',
        DeviceAutocomplete.as_view(),
        name='device_autocomplete',
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
    url(
        r'^get_versions/$',
        RedirectView.as_view(url=reverse_lazy('get_projects'))
    ),
    url(
        r'^chart/version_computer/$',
        RedirectView.as_view(url=reverse_lazy('stats_dashboard'))
    ),
]
