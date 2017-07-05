# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import alerts

urlpatterns = [
    url(r'^alerts/$', alerts, name='alerts'),
]
