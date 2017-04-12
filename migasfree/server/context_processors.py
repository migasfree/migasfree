# -*- coding: utf-8 -*-

from migasfree import __version__

from .models import Project, Query


def query_names(request):
    return {'query_names': Query.get_query_names()}


def project_names(request):
    try:
        current = request.user.userprofile.project
    except:
        current = ''

    return {
        'project_names': Project.get_project_names(),
        'current_project': current
    }


def migasfree_version(request):
    return {'migasfree_version': __version__}
