# -*- coding: UTF-8 -*-

from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):
    # https://code.djangoproject.com/ticket/16626

    @classmethod
    def as_view(cls):
        return login_required(super(LoginRequiredMixin, cls).as_view())
