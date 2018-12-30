# -*- coding: utf-8 -*-

HOURLY_RANGE = 3  # days
DAILY_RANGE = 35  # days
MONTHLY_RANGE = 18  # months

from .checkings import alerts

from .dashboard import stats_dashboard

from .devices import devices_summary, device_models_summary

from .schedules import project_schedule_delays, provided_computers_by_delay

from .syncs import SyncStatsViewSet, synchronized_daily, synchronized_monthly

from .software import stores_summary, packages_summary, applications_summary

from .computers import computers_summary

from .deployments import deployments_summary

from .sources import sources_summary

from .attributes import attributes_summary, tags_summary

from .events import (
    syncs_summary, migrations_summary, status_logs_summary,
    faults_summary, errors_summary, notifications_summary,
)
