# -*- coding: utf-8 -*-

# import order is very important!!!

from migasfree.server.views.stats import chart, \
    daily_updated, delay_schedule, hourly_updated, monthly_updated, \
    version_computer
from migasfree.server.views.queries import query, \
    computer_messages, server_messages
from migasfree.server.views.hardware import hardware, hardware_resume, \
    load_hw, process_hw
from migasfree.server.views.devices import device, load_devices
from migasfree.server.views.repository import create_repositories, create_repos
from migasfree.server.views.client_api import api
from migasfree.server.views.public_api import get_versions
from migasfree.server.views.packages import change_version, info
from migasfree.server.views.dashboard import status, ajax_status, \
    get_current_status
from migasfree.server.views.login import login

