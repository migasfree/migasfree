# -*- coding: utf-8 -*-

"""
Django settings for migasfree project
"""

import os
import django
import django.conf.global_settings as DEFAULT_SETTINGS

if django.get_version() < '1.4':
    print('Migasfree requires Django 1.4. Please, update it.')
    exit(1)

STATICFILES_DIRS = (
    ("admin", os.path.join(
        os.path.dirname(os.path.abspath(django.__file__)),
        'contrib/admin/static/admin'
    )),
)

MIGASFREE_AUTOREGISTER = True

MIGASFREE_TMP_DIR = '/tmp/migasfree-server'
MIGASFREE_SECONDS_MESSAGE_ALERT = 1800
MIGASFREE_ORGANIZATION = 'My Organization'
MIGASFREE_APP_DIR = os.path.dirname(__file__)

# development environment
TEMPLATE_DEBUG = DEBUG = True

MIGASFREE_PROJECT_DIR = os.path.dirname(os.getcwd())
MIGASFREE_DB_DIR = '../..'
MIGASFREE_REPO_DIR = os.path.join(MIGASFREE_PROJECT_DIR, 'repo')
MIGASFREE_KEYS_DIR = os.path.join(MIGASFREE_APP_DIR, 'keys')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(MIGASFREE_DB_DIR, 'migasfree.db'),
    }
}

DEVELOPMENT = True

if not os.path.exists(os.path.join(MIGASFREE_PROJECT_DIR, 'repo')):
    # production environment
    TEMPLATE_DEBUG = DEBUG = False

    MIGASFREE_PROJECT_DIR = '/usr/share/migasfree-server'
    MIGASFREE_DB_DIR = MIGASFREE_PROJECT_DIR
    MIGASFREE_REPO_DIR = '/var/migasfree/repo'
    MIGASFREE_KEYS_DIR = os.path.join(MIGASFREE_PROJECT_DIR, 'keys')

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

    DEVELOPMENT = False

# PERIOD HARDWARE CAPTURE (DAYS)
MIGASFREE_HW_PERIOD = 30

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

FIRST_DAY_OF_WEEK = 1
DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

STATIC_ROOT = MIGASFREE_REPO_DIR
STATIC_URL = '/repo/'

FILE_UPLOAD_TEMP_DIR = MIGASFREE_TMP_DIR

LOGIN_REDIRECT_URL = '/'

LOCALE_PATHS = (
    os.path.join(MIGASFREE_APP_DIR, 'locale'),
)

ADMIN_SITE_ROOT_URL = '/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'p*2#s)b48j^&rm-kr&=f0a2#9^*p3gpd(21!$6o@yn4wd21-(u'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'migasfree.middleware.threadlocals.ThreadLocals',
)

ROOT_URLCONF = 'migasfree.urls'

TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    "migasfree.server.context_processors.query_names",
    "migasfree.server.context_processors.version_names",
    "migasfree.server.context_processors.current_status",
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(MIGASFREE_APP_DIR, 'templates'),
)

DEFAULT_CHARSET = 'utf-8'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.admindocs',
    'django.contrib.messages',
    'migasfree.server',
    'ajax_select',
    'south',
)

# DEFINE THE SEARCH CHANNELS:

AJAX_LOOKUP_CHANNELS = {
    # simplest way, automatically construct a search channel
    # by passing a dictionary
    'label': {'model': 'server.label', 'search_field': 'name'},

    # Custom channels are specified with a tuple
    # channel: ( module.where_lookup_is, ClassNameOfLookup )
    'attribute': ('migasfree.server.lookups', 'AttributeLookup'),
    'package': ('migasfree.server.lookups', 'PackageLookup'),
}

AJAX_SELECT_BOOTSTRAP = True
# True: [easiest]
#   use the admin's jQuery if present else load from jquery's CDN
#   use jqueryUI if present else load from jquery's CDN
#   use jqueryUI theme if present else load one from jquery's CDN
# False/None/Not set: [default]
#   you should include jQuery, jqueryUI + theme in your template

AJAX_SELECT_INLINES = 'inline'
# 'inline': [easiest]
#   includes the js and css inline
#   this gets you up and running easily
#   but on large admin pages or with higher traffic it will be a bit wasteful.
# 'staticfiles':
#   @import the css/js from {{STATIC_URL}}/ajax_selects
#     using django's staticfiles app
#   requires staticfiles to be installed and to run its management command
#     to collect files
#   this still includes the css/js multiple times and is thus inefficient
#   but otherwise harmless
# False/None: [default]
#   does not inline anything. include the css/js files in your compressor stack
#   or include them in the head of the admin/base_site.html template
#   this is the most efficient but takes the longest to configure

# when using staticfiles you may implement your own ajax_select.css
# and customize to taste


###########################################################################

#  STANDARD CONFIG SETTINGS ###############################################

# import local settings if exists
# http://stackoverflow.com/a/1527240
def _load_settings(path):
    if os.path.exists(path):
        print "Loading configuration from %s" % (path)
        settings = {}
        # execfile can't modify globals directly, so we will load them manually
        execfile(path, globals(), settings)
        for setting in settings:
            globals()[setting] = settings[setting]

_load_settings("/etc/migasfree-server/settings.py")
