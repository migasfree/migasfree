# -*- coding: utf-8 -*-

from migasfree import __version__

from .models import Version, get_query_names, UserProfile


def query_names(request):
    return {'query_names': get_query_names()}


def version_names(request):
    try:
        current = UserProfile.objects.get(id=request.user.id).version.name
    except:
        current = ''

    return {
        'version_names': Version.get_version_names(),
        'current_version': current
    }


def migasfree_version(request):
    return {'migasfree_version': __version__}
