# -*- coding: utf-8 -*-

"""
Django settings for migasfree project

Please, don't edit this file
Override or include settings at /etc/migasfree-server/settings.py
"""

import os

import django
import django.conf.global_settings as DEFAULT_SETTINGS

from django.contrib import messages

from .migasfree import BASE_DIR, MIGASFREE_TMP_DIR

if django.VERSION < (1, 9, 0, 'final'):
    print('Migasfree requires Django 1.9.0. Please, update it.')
    exit(1)

ADMINS = (
    ('Your name', 'your_name@example.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

FIRST_DAY_OF_WEEK = 1
DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

STATIC_URL = '/static/'
MEDIA_URL = '/repo/'

FILE_UPLOAD_TEMP_DIR = MIGASFREE_TMP_DIR

LOGIN_REDIRECT_URL = '/'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

ADMIN_SITE_ROOT_URL = '/admin/'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'migasfree.middleware.threadlocals.ThreadLocals',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS
            + [
                'migasfree.server.context_processors.query_names',
                'migasfree.server.context_processors.version_names',
                'migasfree.server.context_processors.migasfree_version',
            ],
        },
    },
]

DEFAULT_CHARSET = 'utf-8'

ROOT_URLCONF = 'migasfree.urls'

MESSAGE_TAGS = {
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
    messages.SUCCESS: 'success',
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'migasfree.server',  # before admin apps to override
    'django_admin_bootstrapped',  # before django.contrib.admin to override
    'autocomplete_light',  # before django.contrib.admin
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.admindocs',
    'ajax_select',
    'migasfree.flot',
    'import_export',
)

DAB_FIELD_RENDERER = 'django_admin_bootstrapped.renderers.BootstrapFieldRenderer'

# http://docs.python.org/2/howto/logging-cookbook.html
# http://docs.python.org/2/library/logging.html#logrecord-attributes
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(funcName)s - %(message)s',
        },
        'simple': {
            'format': '%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(MIGASFREE_TMP_DIR, 'migasfree.log'),
        },
    },
    'loggers': {
        'migasfree': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
        },
    },
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)
