# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.contrib import auth
from django.shortcuts import render, redirect
from django.urls import reverse
from ..models import UserProfile

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

    # check domain_preference for domain admin
    user_profile = UserProfile.objects.get(pk=user.pk)
    if not user_profile.is_superuser and user_profile.is_domain_admin():
        if not user_profile.domain_preference or user_profile.domain_preference not in user_profile.domains.all():
            user_profile.domain_preference = user_profile.domains.all()[0]
            user_profile.save()

    return redirect(request.GET.get('next', reverse('bootstrap')))
