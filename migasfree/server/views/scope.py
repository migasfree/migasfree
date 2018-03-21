# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from ..models import Scope, UserProfile


@login_required
def change_scope(request):
    if request.method == 'GET':
        if int(request.GET.get('scope')) == 0:  # all
            scope = 0
        else:
            scope = get_object_or_404(Scope, pk=request.GET.get('scope'))

        user_profile = UserProfile.objects.get(id=request.user.id)
        user_profile.update_scope(scope)

    next_page = request.META.get('HTTP_REFERER', reverse('bootstrap'))
    if next_page.find(reverse('admin:server_deployment_changelist')) > 0:
        next_page = '%s?active__exact=1' \
            % reverse('admin:server_deployment_changelist')

    return HttpResponseRedirect(next_page)
