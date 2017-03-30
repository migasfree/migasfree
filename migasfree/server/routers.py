# -*- coding: utf-8 -*-

from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(r'attributes', views.AttributeViewSet)
router.register(r'checkings', views.CheckingViewSet)
router.register(r'computers', views.ComputerViewSet)
router.register(
    r'computers',
    views.HardwareComputerViewSet,
    base_name='computers-hardware'
)
router.register(r'errors', views.ErrorViewSet)
router.register(r'fault-definitions', views.FaultDefinitionViewSet)
router.register(r'faults', views.FaultViewSet)
router.register(r'hardware', views.HardwareViewSet)
router.register(r'migrations', views.MigrationViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'packages', views.PackageViewSet)
router.register(r'platforms', views.PlatformViewSet)
router.register(r'properties', views.PropertyViewSet)
router.register(r'pms', views.PmsViewSet)
router.register(r'repositories', views.RepositoryViewSet)
router.register(r'schedules', views.ScheduleViewSet)
router.register(r'status-logs', views.StatusLogViewSet)
router.register(r'stores', views.StoreViewSet)
router.register(r'syncs', views.SynchronizationViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'versions', views.VersionViewSet)
