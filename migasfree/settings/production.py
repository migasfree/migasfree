# -*- coding: utf-8 -*-

from .migasfree import *
from .base import *
from .functions import secret_key

# production environment
TEMPLATE_DEBUG = DEBUG = False

ALLOWED_HOSTS = ['*']

STATIC_ROOT = '/var/migasfree/static'

MIGASFREE_DB_DIR = '/usr/share/migasfree-server'
MIGASFREE_REPO_DIR = '/var/migasfree/repo'
MIGASFREE_KEYS_DIR = os.path.join(MIGASFREE_DB_DIR, 'keys')

SECRET_KEY = secret_key(MIGASFREE_KEYS_DIR)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'migasfree',
        'USER': 'migasfree',
        'PASSWORD': 'migasfree',
        'HOST': '',
        'PORT': '',
    }
}

###########################################################################

#  STANDARD CONFIG SETTINGS ###############################################

# import local settings if exists
# http://stackoverflow.com/a/1527240
def _load_settings(path):
    if os.path.exists(path):
        # Loading configuration from path
        settings = {}
        # execfile can't modify globals directly, so we will load them manually
        execfile(path, globals(), settings)
        for setting in settings:
            globals()[setting] = settings[setting]

_load_settings("/etc/migasfree-server/settings.py")
