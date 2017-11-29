# -*- coding: utf-8 -*-

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'apps', views.ApplicationViewSet)
router.register(r'packages', views.PackagesByProjectViewSet)
router.register(r'policies', views.PolicyViewSet)
router.register(r'policy-groups', views.PolicyGroupViewSet)
