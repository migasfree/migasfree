# -*- coding: utf-8 -*-

"""
set up our URLs
"""

import os
import settings

from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from ajax_select import urls as ajax_select_urls

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^admin/lookups/', include(ajax_select_urls)),

    url(r'', include('migasfree.server.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'^repo/(?P<path>.*)$', 'serve', {
            'document_root': settings.STATIC_ROOT,
            'show_indexes': True
        }),

        (r'^media/(?P<path>.*)$', 'serve', {
            'document_root': os.path.join(os.path.dirname(__file__), 'media'),
            'show_indexes': True
        }),
    )
