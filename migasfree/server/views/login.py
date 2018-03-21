# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.contrib import auth
from django.shortcuts import render, redirect
from django.urls import reverse


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

    auth.login(request, user)

    return redirect(request.GET.get('next', reverse('bootstrap')))
