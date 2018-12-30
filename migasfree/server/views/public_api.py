# -*- coding: utf-8 -*-

import json

from django.conf import settings
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render

from rest_framework.decorators import permission_classes
from rest_framework import permissions, views
from rest_framework.response import Response
from rest_framework import status

from ..models import Platform, Project, Deployment
from ..api import get_computer
from ..utils import uuid_validate
from ..secure import gpg_get_key


def get_projects(request):
    result = []
    for plat in Platform.objects.all():
        element = {
            "platform": plat.name,
            "projects": []
        }
        for prj in Project.objects.filter(platform=plat):
            element["projects"].append({"name": prj.name})

        result.append(element)

    return JsonResponse(result, safe=False)


def get_computer_info(request, uuid=None):
    if uuid:
        _uuid = uuid_validate(uuid)
    else:
        _uuid = uuid_validate(request.GET.get('uuid', ''))
    _name = request.GET.get('name', '')
    if _uuid == "":
        _uuid = _name

    computer = get_computer(_name, _uuid)
    if not computer:
        raise Http404

    result = {
        'id': computer.id,
        'uuid': computer.uuid,
        'name': computer.__str__(),
        'helpdesk': settings.MIGASFREE_HELP_DESK,
        'server': request.META.get('HTTP_HOST'),
        'tags': [u"{}-{}".format(tag.property_att.prefix, tag.value) for tag in computer.tags.all()],
        'available_tags': {},
    }
    result["search"] = result[settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0]]

    for deploy in Deployment.objects.filter(
        project=computer.project, enabled=True
    ):
        for tag in deploy.included_attributes.filter(
            property_att__sort='server', property_att__enabled=True
        ):
            if tag.property_att.name not in result["available_tags"]:
                result["available_tags"][tag.property_att.name] = []

            value = u"{}-{}".format(tag.property_att.prefix, tag.value)
            if value not in result["available_tags"][tag.property_att.name]:
                result["available_tags"][tag.property_att.name].append(value)

    return JsonResponse(result)


def computer_label(request, uuid=None):
    """
    To Print a Computer Label
    """
    if not uuid:
        uuid = request.GET.get('uuid', '')

    computer_info = json.loads(get_computer_info(request, uuid).content)

    return render(
        request,
        'computer_label.html',
        computer_info
    )


def get_key_repositories(request):
    """
    Returns the repositories public key
    """
    return HttpResponse(
        gpg_get_key("migasfree-repository"),
        content_type="text/plain"
    )


def get_sourcefile(request):
    from django.conf import settings
    import os
    from urllib2 import urlopen, URLError, HTTPError
    from wsgiref.util import FileWrapper
    from django.http import HttpResponse
    from migasfree.server.models import Source
    import time

    source = None

    _path = request.get_full_path()
    project_name = _path.split("/")[2]
    source_name = _path.split("/")[4]
    resource = _path.split("/src/"+ project_name+"/SOURCES/"+source_name+"/")[1]

    _file_local = os.path.join(settings.MIGASFREE_PUBLIC_DIR, _path.split("/src/")[1])

    if not (_file_local.endswith(".deb") or _file_local.endswith(".rpm")): # is a metadata file
        # get source
        source = Source.objects.get(project__name=project_name, name=source_name)

        if not source.frozen:
            # expired metadata
            if os.path.exists(_file_local) and (
                source.expire <= 0 or
                (time.time() - os.stat(_file_local).st_mtime) / (60 * source.expire) > 1
            ):
                os.remove(_file_local)

    if not os.path.exists(_file_local):
        if not os.path.exists(os.path.dirname(_file_local)):
            os.makedirs(os.path.dirname(_file_local))  # Make path local

        if not source:
            source = Source.objects.get(project__name=project_name, name=source_name)

        url = "{}/{}".format(str(source.base), resource)

        try:
            f = urlopen(url)

            # Open our local file for writing
            with open(_file_local, "wb") as local_file:
                contenido = f.read()
                local_file.write(contenido)

        #handle errors
        except HTTPError, e:
            return HttpResponse("HTTP Error:"+ str(e.code) + ' ' + url, status=e.code)


        except URLError, e:
            return HttpResponse("URL Error:"+ str(e.reason) + ' ' + url, status=e.code)

    if os.path.isfile(_file_local):
        wrapper = FileWrapper(file(_file_local))
        response = HttpResponse(wrapper, content_type="application/octet-stream")
        response["Content-Disposition"] = "attachment; filename=%s" % os.path.basename(_file_local)
        response['Content-Length'] = os.path.getsize(_file_local)
    else:
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
    return response


@permission_classes((permissions.AllowAny,))
class RepositoriesUrlTemplateView(views.APIView): # compatibility for migasfree-clients <= 4.16
    def post(self, request, format=None):
        """
        Returns the repositories URL template
        """
        protocol = 'https' if request.is_secure() else 'http'

        return Response(
            '{}://{{server}}{}{{project}}/{}'.format(
                protocol,
                settings.MEDIA_URL,
                Project.REPOSITORY_TRAILING_PATH
            ),
            content_type='text/plain'
        )


@permission_classes((permissions.AllowAny,))
class ServerInfoView(views.APIView):
    def post(self, request, format=None):
        """
        Returns server info
        """
        from ... import __version__, __author__, __contact__, __homepage__

        info = {
            'version': __version__,
            'author': __author__,
            'contact': __contact__,
            'homepage': __homepage__,
        }

        return Response(info)
