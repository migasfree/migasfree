# -*- coding: utf-8 -*-

from migasfree.server.models import get_version_names, get_query_names, \
    UserProfile
from migasfree.server.views import get_current_status


def query_names(request):
    return {'query_names': get_query_names()}


def version_names(request):
    try:
        current = UserProfile.objects.get(id=request.user.id).version.name
    except:
        current = ''

    return {
        'version_names': get_version_names(),
        'current_version': current
    }


def current_status(request):
    #return {'current_status': get_current_status()}
    return {'current_status': ''}
