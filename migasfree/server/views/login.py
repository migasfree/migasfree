# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse

from ..models import Version, UserProfile


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


@login_required
def preferences(request):
    if request.method == 'GET':
        return render(
            request,
            'preferences.html',
        )

    version = get_object_or_404(Version, pk=request.POST.get('version', 0))
    user_profile = UserProfile.objects.get(id=request.user.id)
    user_profile.update_version(version)

    messages.success(request, _("Preferences changed"))

    success_url = '%s?active__exact=1&version__id__exact=%d' % (
        reverse('admin:server_repository_changelist'),
        version.id
    )

    return redirect(success_url)
