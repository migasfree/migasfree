# -*- coding: utf-8 *-*
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from migasfree.server.models import  DeviceModel, DeviceConnection
from migasfree.server.functions import *

def connections_model(request):
    json = "{}"
    model_id = request.GET.get('id', '')
    lst_id = s2l(vl2s(DeviceModel.objects.get(id=model_id).connections))
    json = serializers.serialize("json", DeviceConnection.objects.filter(id__in =lst_id))
    return HttpResponse(json, mimetype="application/javascript")
