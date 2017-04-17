# -*- coding: utf-8 -*-

from .migasfree import *
from .base import *
from .functions import secret_key

# production environment
DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
]

ALLOWED_HOSTS = ['*']

MIGASFREE_PUBLIC_DIR = '/var/migasfree/repo'
MIGASFREE_KEYS_DIR = '/usr/share/migasfree-server/keys'

STATIC_ROOT = '/var/migasfree/static'
MEDIA_ROOT = MIGASFREE_PUBLIC_DIR

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

try:
    execfile(MIGASFREE_SETTINGS_OVERRIDE, globals(), locals())
except IOError:
    pass
