# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from ..models import Domain, UserProfile


@login_required
def change_domain(request):
    if request.method == 'GET':
        if int(request.GET.get('domain')) == 0:  # All
            domain = 0
        else:
            domain = get_object_or_404(Domain, pk=request.GET.get('domain'))

        user_profile = UserProfile.objects.get(id=request.user.id)

        if user_profile.is_domain_admin():
            if domain == 0 or domain not in user_profile.domains.all():
                raise PermissionDenied

        user_profile.update_domain(domain)
        user_profile.update_scope(0)

    next_page = request.META.get('HTTP_REFERER', reverse('bootstrap'))
    if next_page.find(reverse('admin:server_deployment_changelist')) > 0:
        next_page = '%s?active__exact=1' \
            % reverse('admin:server_deployment_changelist')

    return HttpResponseRedirect(next_page)
