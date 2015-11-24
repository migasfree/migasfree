# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

import autocomplete_light.shortcuts as al
# import every app/autocomplete_light_registry.py
al.autodiscover()

from django.contrib import admin
admin.autodiscover()

from ajax_select import urls as ajax_select_urls

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
    url(r'', include('migasfree.server.urls')),
    url(r'^apps/', include('migasfree.apps.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^autocomplete/', include('autocomplete_light.urls')),

    url(r'^rest/', include('migasfree.rest.urls')),

    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
)

if settings.DEBUG and settings.STATIC_ROOT is not None:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )

if settings.DEBUG and settings.MEDIA_ROOT is not None:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
        show_indexes=True
    )
