# -*- coding: utf-8 -*-

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MIGASFREE_AUTOREGISTER = True

MIGASFREE_COMPUTER_SEARCH_FIELDS = ('id', 'name', )

MIGASFREE_SECONDS_MESSAGE_ALERT = 1800
MIGASFREE_ORGANIZATION = 'My Organization'
MIGASFREE_HELP_DESK = "Put here how you want to be found"

MIGASFREE_APP_DIR = BASE_DIR
MIGASFREE_PROJECT_DIR = os.path.dirname(MIGASFREE_APP_DIR)
MIGASFREE_TMP_DIR = '/tmp'

# MIGASFREE_REMOTE_ADMIN_LINK
# Variables can be: {{computer.<FIELD>}} and {{<<PROPERTYPREFIX>>}}
# Samples:
#    MIGASFREE_REMOTE_ADMIN_LINK = "https://myserver/?computer={{computer.name}}&port={{PRT}}"
#    MIGASFREE_REMOTE_ADMIN_LINK = "ssh://user@{{computer.ip}} vnc://{{computer.ip}}"
MIGASFREE_REMOTE_ADMIN_LINK = ""

MIGASFREE_INVALID_UUID = [
    "03000200-0400-0500-0006-000700080008",  # ASROCK
    "00000000-0000-0000-0000-000000000000",
    "00000000-0000-0000-0000-FFFFFFFFFFFF"
]

# Notifications
MIGASFREE_NOTIFY_NEW_COMPUTER = False
MIGASFREE_NOTIFY_CHANGE_UUID = False
MIGASFREE_NOTIFY_CHANGE_NAME = False
MIGASFREE_NOTIFY_CHANGE_IP = False

# PERIOD HARDWARE CAPTURE (DAYS)
MIGASFREE_HW_PERIOD = 30

# DEFAULT COMPUTER STATUS
# Values: 'intended', 'reserved', 'unknown', 'in repair', 'available' or 'unsubscribed'
MIGASFREE_DEFAULT_COMPUTER_STATUS = 'intended'
