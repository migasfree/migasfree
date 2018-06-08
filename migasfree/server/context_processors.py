# -*- coding: utf-8 -*-

from .. import __version__

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .models import Domain, Scope, Query


ALL_RANGE = _("all")


def query_names(request):
    return {'query_names': Query.get_query_names()}


def scope_names(request):
    try:
        current = request.user.userprofile.scope_preference
    except AttributeError:
        current = None

    if not current:
        current = ALL_RANGE

    lst = [[0, ALL_RANGE]]
    try:
        for scope in list(
            Scope.objects.filter(
                user=request.user, domain=request.user.userprofile.domain_preference
            ).order_by('name').values_list('id', 'name')
        ):
            lst.append(scope)
    except AttributeError:
        return {}

    return {
        'scope_names': lst,
        'current_scope': current
    }


def domain_names(request):
    try:
        current = request.user.userprofile.domain_preference
    except AttributeError:
        current = None

    if not current:
        current = ALL_RANGE.upper()

    lst = []
    try:
        user = request.user.userprofile
        if user.is_superuser or len(user.domains.all()) == 0:
            lst.append([0, ALL_RANGE.upper()])
            for domain in list(Domain.objects.order_by('name').values_list('id', 'name')):
                lst.append(domain)
        else:
            for domain in list(user.domains.order_by('name').values_list('id', 'name')):
                lst.append(domain)
    except AttributeError:
        return {}

    return {
        'domain_names': lst,
        'current_domain': current
    }


def migasfree_version(request):
    return {'migasfree_version': __version__}


def global_settings(request):
    # return any necessary values
    return {
        'EMAIL_HOST_USER': settings.EMAIL_HOST_USER,
    }
