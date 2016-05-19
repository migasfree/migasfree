# -*- coding: utf-8 -*-

from .development import *

JENKINS_TASKS = (
    #'django_jenkins.tasks.with_coverage',
    #'django_jenkins.tasks.django_tests',
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pyflakes',
)

INSTALLED_APPS += ('django_jenkins',)
