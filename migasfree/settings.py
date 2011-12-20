# -*- coding: utf-8 -*-

"""
Django settings for migasfree project
"""

import os

MIGASFREE_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIGASFREE_DB_DIR = '/var/tmp'
MIGASFREE_DB_NAME = 'migasfree'
MIGASFREE_APP_DIR = '/usr/share/migasfree-server'
MIGASFREE_REPO_DIR = '/var/migasfree/repo'
MIGASFREE_TMP_DIR = '/tmp/migasfree-server'
MIGASFREE_SECONDS_MESSAGE_ALERT = 1800
MIGASFREE_ORGANIZATION = "My Organization"
MIGASFREE_HOSTNAME = 'www.myorganization.com'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

FIRST_DAY_OF_WEEK = 1

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(MIGASFREE_DB_DIR, MIGASFREE_DB_NAME),  # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': MIGASFREE_DB_NAME,  # Or path to database file if using sqlite3.
        'USER': 'migasfree',                      # Not used with sqlite3.
        'PASSWORD': 'migasfree',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
"""

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#LANGUAGE_CODE = 'es-ES'
LANGUAGE_CODE = 'en-us'


SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

STATIC_ROOT = MIGASFREE_REPO_DIR
STATIC_URL = 'http://%s/repo' % MIGASFREE_HOSTNAME

FILE_UPLOAD_TEMP_DIR = MIGASFREE_TMP_DIR
LOGIN_REDIRECT_URL = '/migasfree/main/'

#LOCALE_PATHS = (
#    '/usr/share/locale'
#)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'
ADMIN_SITE_ROOT_URL = '/migasfree/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'p*2#s)b48j^&rm-kr&=f0a2#9^*p3gpd(21!$6o@yn4wd21-(u'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'migasfree.middleware.threadlocals.ThreadLocals',
)

ROOT_URLCONF = 'migasfree.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(MIGASFREE_PROJECT_DIR, 'templates'),
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
    'migasfree.server',
    'ajax_select',
)

# DEFINE THE SEARCH CHANNELS:

AJAX_LOOKUP_CHANNELS = {
    # simplest way, automatically construct a search channel by passing a dictionary
    'label'  : {'model':'server.label', 'search_field':'name'},
    
    # Custom channels are specified with a tuple
    # channel: ( module.where_lookup_is, ClassNameOfLookup )
    'attribute' : ('migasfree.server.lookups', 'AttributeLookup'),
    'package' : ('migasfree.server.lookups', 'PackageLookup'),


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
#   @import the css/js from {{STATIC_URL}}/ajax_selects using django's staticfiles app
#   requires staticfiles to be installed and to run its management command to collect files
#   this still includes the css/js multiple times and is thus inefficient
#   but otherwise harmless
# False/None: [default]
#   does not inline anything. include the css/js files in your compressor stack
#   or include them in the head of the admin/base_site.html template
#   this is the most efficient but takes the longest to configure

# when using staticfiles you may implement your own ajax_select.css and customize to taste



###########################################################################

#  STANDARD CONFIG SETTINGS ###############################################
