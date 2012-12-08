# -*- coding: utf-8 -*-

from migasfree.server.views.stats import chart, \
    daily_updated, delay_schedule, hourly_updated, monthly_updated, \
    version_computer
from migasfree.server.views.queries import query, \
    computer_messages, server_messages
from migasfree.server.views.hardware import hardware, hardware_resume, \
    load_hw, process_hw
from migasfree.server.views.devices import device, load_devices
from migasfree.server.views.client_api import api
from migasfree.server.views.packages import change_version, info
from migasfree.server.views.dashboard import main, ajax_status
from migasfree.server.views.login import login
from migasfree.server.views.repository import createrepositories
