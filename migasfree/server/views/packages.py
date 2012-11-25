# -*- coding: utf-8 -*-

import os

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django import forms

from migasfree.settings import MIGASFREE_REPO_DIR
from migasfree.server.models import *
from migasfree.server.forms import ParametersForm


@login_required
def info(request, package):  # package info
    try:
        if request.GET.get('version'):
            version = Version.objects.get(name=request.GET.get('version'))
        else:
            version = UserProfile.objects.get(id=request.user.id).version
    except:
        return HttpResponse(
            'No version to find info.',
            mimetype="text/plain"
        )  # FIXME

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
            'info_package.html',
            {
                "title": _("Information of Package"),
                "contentpage": ret,
            }
        )

    if os.path.isdir(path):
        # NAVIGATION FOR FOLDERS
        vl_fields = []
        filters = []
        filters.append(package)
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
            'info_folder.html',
            {
                "title": _("Information of Package"),
                "description": _("VERSION: %s") % version.name,
                "filters": filters,
                "query": vl_fields,
            }
        )

    return HttpResponse(
        'No package info exists.',
        mimetype="text/plain"
    )  # FIXME


@login_required()
def change_version(request):
    def form_params_version():
        class MyForm(ParametersForm):
            version = forms.ModelChoiceField(Version.objects.all())

        return MyForm

    if request.method == 'POST':
        parameters = {}
        for p in request.POST:
            parameters[p] = request.POST.get(p)

        o_userprofile = UserProfile.objects.get(id=request.user.id)
        o_userprofile.version = Version.objects.get(id=parameters["version"])
        o_userprofile.save()

        return HttpResponseRedirect(reverse('bootstrap'))
    else:
        try:
            oversion = UserProfile.objects.get(id=request.user.id).version.id
        except:
            oversion = None

        dic_initial = {
            'user_version': oversion,
            'version': oversion
        }

        g_form_param = form_params_version()(initial=dic_initial)
        request.session['LastUrl'] = request.META.get(
            'HTTP_REFERER', reverse('bootstrap')
        )

        return render(
            request,
            'parameters.html',
            {
                'form': g_form_param,
                'title': _("Change version for %s") % request.user.username,
            }
        )
