# -*- coding: utf-8 -*-

HOURLY_RANGE = 3  # days
DAILY_RANGE = 35  # days
MONTHLY_RANGE = 18  # months

from .checkings import alerts

from .dashboard import (
    stats_dashboard,
)

from .devices import devices_summary

from .schedules import project_schedule_delays, provided_computers_by_delay

from .syncs import SyncStatsViewSet, synchronized_daily, synchronized_monthly
