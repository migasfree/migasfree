# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings

from ..models import Platform, Version, Deployment
from ..api import get_computer
from ..functions import uuid_validate
from ..security import gpg_get_key


def get_versions(request):
    result = []
    for plat in Platform.objects.all():
        element = {
            "platform": plat.name,
            "versions": []
        }
        for ver in Version.objects.filter(platform=plat):
            element["versions"].append({"name": ver.name})

        result.append(element)

    return JsonResponse(result, safe=False)


def get_computer_info(request):
    _uuid = uuid_validate(request.GET.get('uuid', ''))
    _name = request.GET.get('name', '')
    if _uuid == "":
        _uuid = _name

    computer = get_computer(_name, _uuid)

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
        element.append("{}-{}".format(tag.property_att.prefix, tag.value))
    result["tags"] = element

    result["available_tags"] = {}
    for deploy in Deployment.objects.all().filter(
        version=computer.version, enabled=True
    ):
        for tag in deploy.included_attributes.all().filter(
            property_att__tag=True, property_att__active=True
        ):
            if tag.property_att.name not in result["available_tags"]:
                result["available_tags"][tag.property_att.name] = []

            value = "{}-{}".format(tag.property_att.prefix, tag.value)
            if value not in result["available_tags"][tag.property_att.name]:
                result["available_tags"][tag.property_att.name].append(value)

    return JsonResponse(result)


def computer_label(request):
    """
    To Print a Computer Label
    """
    return render(
        request,
        'computer_label.html',
        json.loads(get_computer_info(request).content)
    )


def get_key_repositories(request):
    """
    Return the repositories public key
    """
    return HttpResponse(
        gpg_get_key("migasfree-repository"),
        content_type="text/plain"
    )
