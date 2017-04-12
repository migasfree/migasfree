# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse

from ..models import Project, UserProfile


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

    project = None
    success_url = '%s?enabled__exact=1' % reverse('admin:server_deployment_changelist')

    project_id = int(request.POST.get('project', 0))
    if project_id:
        project = get_object_or_404(Project, pk=project_id)
        success_url += '&project__id__exact=%d' % project.id

    user_profile = UserProfile.objects.get(id=request.user.id)
    user_profile.update_project(project)

    messages.success(request, _("Preferences changed"))

    return redirect(success_url)
