# -*- coding: utf-8 -*-

import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render

from rest_framework.decorators import permission_classes
from rest_framework import permissions, views
from rest_framework.response import Response

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
    }
    result["search"] = result[settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0]]

    element = []
    for tag in computer.tags.all():
        element.append(u"{}-{}".format(tag.property_att.prefix, tag.value))
    result["tags"] = element

    result["available_tags"] = {}
    for deploy in Deployment.objects.all().filter(
        project=computer.project, enabled=True
    ):
        for tag in deploy.included_attributes.all().filter(
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
    if computer_info['id'] not in request.user.userprofile.get_computers():
        raise PermissionDenied

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


@permission_classes((permissions.AllowAny,))
class RepositoriesUrlTemplateView(views.APIView):
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
