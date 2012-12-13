# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from migasfree.server.models import UserProfile
from migasfree.server.logic import create_repositories


@login_required
def createrepositories(request):
    """
    Create the files of Repositories in the server
    """
    version = get_object_or_404(UserProfile, id=request.user.id).version

    return render(
        request,
        "info.html",
        {
            "title": _("Create Repositories"),
            "contentpage": create_repositories(version.id),
        }
    )
