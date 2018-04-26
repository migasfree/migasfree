# -*- coding: utf-8 -*-

from rest_framework import routers

from .views import SyncStatsViewSet

router = routers.DefaultRouter()

router.register(r'stats/syncs', SyncStatsViewSet, base_name='stats-syncs')
