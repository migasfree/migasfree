# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse
from django.shortcuts import render
from migasfree.settings import (
    MIGASFREE_HELP_DESK,
    MIGASFREE_COMPUTER_SEARCH_FIELDS
)

from migasfree.server.models import (
    Platform,
    Version,
    Computer,
    Property,
    Attribute
)


def get_versions(request):
    result = []
    _platforms = Platform.objects.all()
    for _platform in _platforms:
        element = {}
        element["platform"] = _platform.name
        element["versions"] = []
        _versions = Version.objects.filter(platform=_platform)
        for _version in _versions:
            element["versions"].append({"name": _version.name})

        result.append(element)

    return HttpResponse(json.dumps(result), mimetype="text/plain")


def get_computer_info(request):
    result = {}
    uuid = request.GET.get('uuid', '')

    if Computer.objects.filter(uuid=uuid):
        computer = Computer.objects.get(uuid=uuid)
        result["id"] = computer.id
        result["uuid"] = computer.uuid
        result["name"] = computer.name
        result["helpdesk"] = MIGASFREE_HELP_DESK
        result["search"] = result[MIGASFREE_COMPUTER_SEARCH_FIELDS[0]]

        element = []
        for tag in computer.tags.all():
            element.append("%s-%s" % (tag.property_att.prefix, tag.value))
        result["tags"] = element
        result["available_tags"] = {}

        for prp in Property.objects.filter(tag=True):
            result["available_tags"][prp.name] = []
            for tag in Attribute.objects.filter(property_att=prp):
                result["available_tags"][prp.name].append("%s-%s" %
                    (prp.prefix, tag.value))

    return HttpResponse(json.dumps(result), mimetype="text/plain")


def computer_label(request):
    """
    To Print a Computer Label
    """
    result = {}
    uuid = request.GET.get('uuid', '')

    if Computer.objects.filter(uuid=uuid):
        computer = Computer.objects.get(uuid=uuid)
        result["id"] = computer.id
        result["uuid"] = computer.uuid
        result["name"] = computer.name
        result["helpdesk"] = MIGASFREE_HELP_DESK
        result["search"] = result[MIGASFREE_COMPUTER_SEARCH_FIELDS[0]]
        return render(
            request,
            'server/computer_label.html',
            result
        )
    else:
        return HttpResponse("", mimetype="text/plain")
