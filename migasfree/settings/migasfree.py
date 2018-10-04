# -*- coding: utf-8 -*-

"""
Please, don't edit this file
Override or include settings at MIGASFREE_SETTINGS_OVERRIDE file
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MIGASFREE_AUTOREGISTER = True

MIGASFREE_COMPUTER_SEARCH_FIELDS = ('id', 'name')

MIGASFREE_SECONDS_MESSAGE_ALERT = 1800
MIGASFREE_ORGANIZATION = 'My Organization'
MIGASFREE_HELP_DESK = 'Put here how you want to be found'

MIGASFREE_SETTINGS_OVERRIDE = '/etc/migasfree-server/settings.py'
MIGASFREE_APP_DIR = BASE_DIR
MIGASFREE_PROJECT_DIR = os.path.dirname(MIGASFREE_APP_DIR)
MIGASFREE_TMP_DIR = '/tmp'

# MIGASFREE_REMOTE_ADMIN_LINK # DEPRECATED
# Variables can be: {{computer.<FIELD>}} and {{<<PROPERTYPREFIX>>}}
# Samples:
#    MIGASFREE_REMOTE_ADMIN_LINK = [
#        "https://myserver/?computer={{computer.name}}&port={{PRT}}"
#    ]
#    MIGASFREE_REMOTE_ADMIN_LINK = [
#        "ssh://user@{{computer.ip_address}}",
#        "vnc://{{computer.ip_address}}"
#    ]
MIGASFREE_REMOTE_ADMIN_LINK = []

"""
MIGASFREE_EXTERNAL_ACTIONS
Sample:

    MIGASFREE_EXTERNAL_ACTIONS = {
        "computer": {
            "ping": {"title": "PING", "description": "check conectivity"},
            "ssh": {"title": "SSH", "description": "remote control vía ssh"},
            "vnc": {"title": "VNC", "description": "remote control vnc", "many": False},
            "sync": {"title": "SYNC", "description": "ssh -> run migasfree -u"},
            "install": {"title": "INSTALL", "description": "ssh -> install a package", "related": ["deployment", "computer"]},
        },
        "error": {
            "clean": {"title": "delete", "description":"delete errors"},
        }
}
"""
MIGASFREE_EXTERNAL_ACTIONS = {}

MIGASFREE_INVALID_UUID = [
    '03000200-0400-0500-0006-000700080008',  # ASROCK
    '00000000-0000-0000-0000-000000000000',
    '00000000-0000-0000-0000-FFFFFFFFFFFF',
]

# Notifications
MIGASFREE_NOTIFY_NEW_COMPUTER = False
MIGASFREE_NOTIFY_CHANGE_UUID = False
MIGASFREE_NOTIFY_CHANGE_NAME = False
MIGASFREE_NOTIFY_CHANGE_IP = False

# PERIOD HARDWARE CAPTURE (DAYS)
MIGASFREE_HW_PERIOD = 30

# Programming Languages for Properties and Fault Definitions
MIGASFREE_PROGRAMMING_LANGUAGES = (
    (0, 'bash'),
    (1, 'python'),
    (2, 'perl'),
    (3, 'php'),
    (4, 'ruby'),
    (5, 'cmd'),
    (6, 'powershell'),
)

# Server Keys
MIGASFREE_PUBLIC_KEY = 'migasfree-server.pub'
MIGASFREE_PRIVATE_KEY = 'migasfree-server.pri'

# Packager Keys
MIGASFREE_PACKAGER_PUB_KEY = 'migasfree-packager.pub'
MIGASFREE_PACKAGER_PRI_KEY = 'migasfree-packager.pri'

# Default Computer Status
# Values: 'intended', 'reserved', 'unknown', 'in repair', 'available' or 'unsubscribed'
MIGASFREE_DEFAULT_COMPUTER_STATUS = 'intended'
