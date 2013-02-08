# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse

from migasfree.server.models import Platform
from migasfree.server.models import Version


def get_versions(request):
    result=[]
    _platforms = Platform.objects.all()
    for _platform in _platforms:
        element={}
        element["platform"] = _platform.name
        element["versions"] = []
        _versions = Version.objects.filter(platform=_platform)
        for _version in _versions:
            element["versions"].append({"name": _version.name})

        result.append(element)

    return HttpResponse(json.dumps(result), mimetype="text/plain")
