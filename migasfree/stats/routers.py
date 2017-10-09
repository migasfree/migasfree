# -*- coding: utf-8 -*-

from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(r'stats/syncs', views.SyncStatsViewSet, base_name='stats-syncs')
