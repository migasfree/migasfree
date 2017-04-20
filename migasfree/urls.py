# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

from ajax_select import urls as ajax_select_urls
from rest_framework.authtoken import views

from server.routers import router
from catalog.routers import router as catalog_router

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^token-auth/$', views.obtain_auth_token),
    url(r'^api/v1/token/', include(router.urls)),
    url(r'^api/v1/public/catalog/', include(catalog_router.urls)),

    url(r'', include('migasfree.server.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),

    url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^markdownx/', include('markdownx.urls')),
]

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
