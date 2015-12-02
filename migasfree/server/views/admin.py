# -*- coding: utf-8 *-*

# FIXME why this file is called admin?

from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from ..models import DeviceModel, DeviceConnection
from ..functions import s2l, vl2s


@login_required
def connections_model(request):
    json = "{}"
    model_id = request.GET.get('id', '')
    if model_id != '':
        lst_id = s2l(vl2s(DeviceModel.objects.get(id=model_id).connections))
        json = serializers.serialize(
            "json",
            DeviceConnection.objects.filter(id__in=lst_id)
        )

    return HttpResponse(json, content_type="application/javascript")
