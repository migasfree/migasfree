# -*- coding: utf-8 -*-

from rest_framework import routers

from . import views

public_router = routers.DefaultRouter()
public_router.register(r'apps', views.ApplicationViewSet)
public_router.register(r'packages', views.PackagesByProjectViewSet)

token_router = routers.DefaultRouter()
token_router.register(r'policies', views.PolicyViewSet)
token_router.register(r'policy-groups', views.PolicyGroupViewSet)
