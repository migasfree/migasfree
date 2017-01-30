# -*- coding: utf-8 -*-

from .development import *

INSTALLED_APPS += ('django_jenkins',)

JENKINS_TASKS = (
    # 'django_jenkins.tasks.django_tests',
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pyflakes',
)
