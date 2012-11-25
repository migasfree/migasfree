# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.contrib import auth
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


def login(request):
    if request.method == 'GET':
        return render(
            request,
            'admin/login.html',
        )

    user = auth.authenticate(
        username=request.POST.get('username'),
        password=request.POST.get('password')
    )
    if user is None or not user.is_active:
        return render(
            request,
            'admin/login.html',
            {'error_message': _('Credentials not valid')}
        )

    # Correct password, and the user is marked "active"
    auth.login(request, user)

    # Redirect to a success page
    return HttpResponseRedirect(
        request.GET.get('next', reverse('bootstrap'))
    )
