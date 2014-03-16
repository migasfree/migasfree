# -*- coding: utf-8 -*-

# import order is very important!!!

from .stats import (
    daily_updated,
    delay_schedule,
    hourly_updated,
    monthly_updated,
    version_computer
)
from .queries import query, computer_messages, server_messages
from .hardware import hardware, hardware_resume, load_hw, process_hw
from .repository import create_physical_repository
from .client_api import api
from .public_api import get_versions, get_computer_info, computer_label
from .packages import change_version, info
from .dashboard import alerts
from .admin import connections_model
from .login import login
from .computer import ComputerDelete, computer_delete_selected
