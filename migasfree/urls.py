# -*- coding: utf-8 -*-

"""
set up our admin URLs
"""

import os

from django.conf.urls.defaults import patterns, include

from django.contrib import admin
admin.autodiscover()

from migasfree.server.views import *
from ajax_select import urls as ajax_select_urls

urlpatterns = patterns(
    '',
    # Example:
    # (r'^migasfree/', include('migasfree.migasfree.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^migasfree/doc/', include('django.contrib.admindocs.urls')),

    (r'^migasfree/admin/lookups/', include(ajax_select_urls)),

    # Uncomment the next line to enable the admin:
    (r'^migasfree/admin/', include(admin.site.urls)),
    # (r'^migasfree/admin/(.*)', admin.site.root),

    # (r'^migasfree/jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
    # (r'^migasfree/jsi18n', 'django.views.i18n.javascript_catalog'),

    # migasfree.server.urls
    #(r'^migasfree', main),
    (r'^$', bootstrap),
    (r'^migasfree/$', bootstrap),
    (r'^migasfree/main/(.*)', main),
    (r'^migasfree/system/(.*)', system),
    (r'^migasfree/query_selection/(.*)', query_selection),
    (r'^migasfree/query/(.*)', query),
    (r'^migasfree/queryMessage/(.*)', query_message),
    (r'^migasfree/queryMessageServer/(.*)', query_message_server),
    (r'^migasfree/update/(.*)', update),
    (r'^migasfree/info/(.*)', info),
    (r'^migasfree/version/(.*)', change_version),
    (r'^migasfree/softwarebase/(.*)', softwarebase),
    (r'^migasfree/message/(.*)', message),
    (r'^migasfree/login/(.*)', login),
    (r'^migasfree/documentation/(.*)', documentation),

    (r'^migasfree/device/(.*)', device),

    (r'^migasfree/chart_selection/(.*)', chart_selection),
    (r'^migasfree/chart/(.*)', chart),
    (r'^migasfree/hourly_updated/(.*)', hourly_updated),
    (r'^migasfree/daily_updated/(.*)', daily_updated),
    (r'^migasfree/monthly_updated/(.*)', monthly_updated),
    (r'^migasfree/delaySchedule/(.*)', delay_schedule),
    (r'^migasfree/version_Computer/(.*)', version_computer),

    (r'^migasfree/hardware/(.*)', hardware),
    (r'^migasfree/hardware_resume/(.*)', hardware_resume),

    # migasfree.api.urls
    # (r'^migasfree/get_device/(.*)', get_device),

    (r'^migasfree/api/(.*)', api),

    (r'^migasfree/uploadPackage/(.*)', upload_package),
    (r'^migasfree/uploadSet/(.*)', upload_set),
    (r'^migasfree/createrepositoriesofpackage/(.*)', createrepositoriesofpackage),
    (r'^migasfree/createrepositories/(.*)', createrepositories),
    (r'^migasfree/directupload/(.*)', directupload),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': os.path.join(os.path.dirname(__file__), 'media')
    }),
)
