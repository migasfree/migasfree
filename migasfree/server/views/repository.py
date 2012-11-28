# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.http import HttpResponse

from migasfree.server.models import UserProfile
from migasfree.server.logic import create_repositories


@login_required
def createrepositories(request):
    """
    Create the files of Repositories in the server
    """
    try:
        version = UserProfile.objects.get(id=request.user.id).version
    except:
        return HttpResponse(
            _('No version to find info.'),
            mimetype="text/plain"
        )  # FIXME

    return render(
        request,
        "info.html",
        {
            "title": _("Create Repositories"),
            "contentpage": create_repositories(version.id),
        }
    )
