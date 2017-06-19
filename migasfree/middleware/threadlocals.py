# coding: utf-8

"""
    threadlocals middleware
    ~~~~~~~~~~~~~~~~~~~~~~~
    make the request object everywhere available (e.g. in model instance).
    based on: http://code.djangoproject.com/wiki/CookBookThreadlocalsAndUser

    Put this into your settings:
    --------------------------------------------------------------------------
        MIDDLEWARE_CLASSES = (
            ...
            'django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware',
            ...
        )
    --------------------------------------------------------------------------


    Usage:
    --------------------------------------------------------------------------
    from django_tools.middlewares import ThreadLocal

    # Get the current request object:
    request = ThreadLocal.get_current_request()

    # You can get the current user directly with:
    user = ThreadLocal.get_current_user()
    --------------------------------------------------------------------------
    :copyleft: 2009-2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.

    Updated for Django >= 1.10: https://gist.github.com/alexpirine/7357232ecf3aab8beb5565b89c587e6d
"""

from threading import local

_thread_locals = local()


def get_current_request():
    """ returns the request object for this thread """
    return getattr(_thread_locals, "request", None)


def get_current_user():
    """ returns the current user, if exist, otherwise returns None """
    request = get_current_request()
    if request:
        return getattr(request, "user", None)


class ThreadLocalMiddleware(object):
    # Copyright (c) Alexandre Syenchuk (alexpirine), 2016

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        return self.get_response(request)
