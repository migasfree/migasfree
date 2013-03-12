# -*- coding: utf-8 -*-

import os

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from migasfree.settings import MIGASFREE_REPO_DIR
from migasfree.server.models import Version, UserProfile
from migasfree.server.functions import run_in_server

import logging
logger = logging.getLogger('migasfree')


@login_required
def info(request, package):  # package info
    #logger.debug('request:' + str(request))
    if request.GET.get('version'):
        version = get_object_or_404(Version, name=request.GET.get('version'))
    else:
        version = get_object_or_404(UserProfile, id=request.user.id).version

    logger.debug('version: ' + version.name)

    if package.endswith('/'):
        package = package[:-1]  # remove trailing slash

    logger.debug('package: ' + package)

    path = os.path.join(MIGASFREE_REPO_DIR, version.name, package)
    if os.path.isfile(path):
        # GET INFORMATION OF PACKAGE
        cmd = 'echo "Version: %s"\n' % version.name
        cmd += 'echo "Package: %s"\n' % package
        cmd += "echo\n"
        cmd += "echo\n"
        cmd += 'PACKAGE=%s\n' % path
        cmd += version.pms.info

        ret = run_in_server(cmd)["out"]

        return render(
            request,
            'server/package_info.html',
            {
                "title": _("Information of Package"),
                "contentpage": ret,
            }
        )

    logger.debug('path:' + path)
    if os.path.isdir(path):
        # folders navigation
        vl_fields = []
        if package > "/":
            vl_fields.append(["folder.png", ".."])

        elements = os.listdir(path)
        elements.sort()
        for e in elements:
            try:
                if os.path.isdir(os.path.join(path, e)):
                    # relative navigation, folders always with trailing slash!!
                    vl_fields.append(["folder.png", e + '/'])
                else:
                    vl_fields.append(["package.png", e])
            except:
                pass

        logger.debug('content:' + str(vl_fields))

        return render(
            request,
            'server/package_folder_info.html',
            {
                "title": _("Information of Package"),
                "description": _("VERSION: %s") % version.name,
                "filters": (package, ),
                "query": vl_fields,
            }
        )

    return render(
        request,
        'error.html',
        {
            'description': _('Error'),
            'contentpage': _('No package info exists')
        }
    )


@login_required()
def change_version(request):
    if request.method == 'POST':
        user_profile = UserProfile.objects.get(id=request.user.id)
        user_profile.version = Version.objects.get(
            id=request.POST.get('version')
        )
        user_profile.save()

    return HttpResponseRedirect(request.META.get(
        'HTTP_REFERER',
        reverse('bootstrap')
    ))
