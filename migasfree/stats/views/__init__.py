# -*- coding: utf-8 -*-

import os

from pygal.style import Style
from django.conf import settings

JS_FILE = 'file://' + os.path.join(
    settings.MIGASFREE_APP_DIR,
    'server',
    'static',
    'js',
    'pygal-tooltips.min.js'
)
BAR_STYLE = Style(
    font_family='Average Sans',
    background='transparent',
    colors=('#edc240', '#5cb85c'),
)
DEFAULT_STYLE = Style(
    font_family='Average Sans',
    background='transparent',
)
WIDTH = 800
HEIGHT = 400
LABEL_ROTATION = 45

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
