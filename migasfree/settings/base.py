# -*- coding: utf-8 -*-

import os
import django

from django.contrib import messages

from .migasfree import BASE_DIR, MIGASFREE_TMP_DIR

if django.VERSION < (1, 11, 0, 'final'):
    print('Migasfree requires Django 1.11.0 at least. Please, update it.')
    exit(1)

ADMINS = (
    ('Your name', 'your_name@example.com'),
)

MANAGERS = ADMINS

TIME_ZONE = 'Europe/Madrid'
USE_TZ = False

FIRST_DAY_OF_WEEK = 1
DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = False

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

STATIC_URL = '/static/'
MEDIA_URL = '/public/'

FILE_UPLOAD_TEMP_DIR = MIGASFREE_TMP_DIR

LOGIN_REDIRECT_URL = '/'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'i18n'),
)

ADMIN_SITE_ROOT_URL = '/admin/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.gzip.GZipMiddleware',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'url_tools.context_processors.current_url',
                'migasfree.server.context_processors.query_names',
                'migasfree.server.context_processors.domain_names',
                'migasfree.server.context_processors.scope_names',
                'migasfree.server.context_processors.migasfree_version',
                'migasfree.server.context_processors.global_settings',
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
    'ajax_select',  # before dal!!!
    'migasfree.server',  # before admin apps to override
    'django_admin_bootstrapped',  # before django.contrib.admin to override
    'dal', 'dal_select2',  # before django.contrib.admin
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.admindocs',
    'import_export',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_filters',
    'rest_framework_swagger',
    'rest_auth',
    'django_filters',
    'corsheaders',
    'form_utils',
    'markdownx',
    'datetimewidget',
    'url_tools',
    'migasfree.catalog',
    'migasfree.stats',
)

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissions',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_filters.backends.RestFrameworkFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
    'VALIDATOR_URL': None,
}

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'migasfree.server.serializers.UserProfileSerializer',
}

DAB_FIELD_RENDERER = 'django_admin_bootstrapped.renderers.BootstrapFieldRenderer'

CORS_ORIGIN_ALLOW_ALL = True

# http://docs.python.org/2/howto/logging-cookbook.html
# http://docs.python.org/2/library/logging.html#logrecord-attributes
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(levelname)s - %(module)s - %(lineno)d '
                      '- %(funcName)s - %(message)s',
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
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(MIGASFREE_TMP_DIR, 'migasfree.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
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

SESSION_COOKIE_NAME = 'migasfree'
# CSRF_COOKIE_NAME = 'csrftoken_migasfree'  # issue with markdownx component :_(
