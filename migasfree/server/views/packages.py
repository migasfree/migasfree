# -*- coding: utf-8 -*-

import os

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from migasfree.settings import MIGASFREE_REPO_DIR
from migasfree.server.models import *
from migasfree.server.functions import run_in_server


@login_required
def info(request, package):  # package info
    if request.GET.get('version'):
        version = get_object_or_404(Version, name=request.GET.get('version'))
    else:
        version = get_object_or_404(UserProfile, id=request.user.id).version

    if package.endswith('/'):
        package = package[:-1]  # remove trailing slash

    path = os.path.join(MIGASFREE_REPO_DIR, version.name, package)
    if os.path.isfile(path):
        # GET INFORMATION OF PACKAGE
        cmd = 'echo "Version: %s"\n' % version.name
        cmd += 'echo "Package: %s"\n' % package[:-1]
        cmd += "echo\n"
        cmd += "echo\n"
        cmd += 'PACKAGE=%s\n' % path[:-1]
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

    if os.path.isdir(path):
        # NAVIGATION FOR FOLDERS
        vl_fields = []
        if package > "/":
            vl_fields.append(["folder.png", ".."])

        elements = os.listdir(path)
        elements.sort()
        for e in elements:
            try:
                # TODO: asegurarse de que esto sirve para identificar
                # si es un archivo o un directorio
                if (os.stat(os.path.join(path, e)).st_mode < 32000):
                    vl_fields.append(["folder.png", e + "/"])
                else:
                    vl_fields.append(["package.png", e + "/"])
            except:
                pass

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
    redirect_to = request.META.get('HTTP_REFERER', reverse('bootstrap'))

    if request.method == 'POST':
        new_version = request.POST.get('version')

        user_profile = UserProfile.objects.get(id=request.user.id)
        user_profile.version = Version.objects.get(id=new_version)
        user_profile.save()

    return HttpResponseRedirect(redirect_to)
