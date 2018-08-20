# -*- coding: UTF-8 -*-

import os

django_settings = os.environ.get('DJANGO_SETTINGS_MODULE', '')

if django_settings != '' and django_settings != 'migasfree.settings':
    exec('from .{} import *'.format(django_settings.split('.')[-1]))
else:
    from .production import *
