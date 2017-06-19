# -*- coding: UTF-8 -*-

import json

from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ..forms import DeviceReplacementForm
from ..models import Device, DeviceModel, DeviceConnection
from ..utils import d2s


@login_required
def connections_model(request):
    response = {}
    model_id = request.GET.get('id', '')

    if model_id != '':
        connections = DeviceConnection.objects.filter(
            id__in=DeviceModel.objects.get(
                id=model_id
            ).connections.values_list(
                'id', flat=True
            )
        )
        response = serializers.serialize("json", connections)

    return JsonResponse(json.loads(response), safe=False)


@login_required
def device_replacement(request):
    if request.method == 'POST':
        form = DeviceReplacementForm(request.POST)
        if form.is_valid():
            source = get_object_or_404(
                Device, pk=form.cleaned_data.get('source').pk
            )
            target = get_object_or_404(
                Device, pk=form.cleaned_data.get('target').pk
            )

            incompatibles = source.incompatible_features(target)
            if not incompatibles:
                Device.replacement(source, target)

                messages.success(request, _('Replacement done.'))
                messages.info(
                    request,
                    '<br/>'.join(sorted(d2s(source.get_replacement_info())))
                )
                messages.info(
                    request,
                    '<br/>'.join(sorted(d2s(target.get_replacement_info())))
                )
            else:
                messages.error(
                    request,
                    _('Replacement is not possible. Please, deallocate all attributes in the features: [%s].')
                    % ",".join(incompatibles))
                messages.error(
                    request,
                    '<br/>'.join(sorted(d2s(source.get_replacement_info()))))
                messages.error(
                    request,
                    '<br/>'.join(sorted(d2s(target.get_replacement_info())))
                )

            return HttpResponseRedirect(reverse('device_replacement'))
    else:
        form = DeviceReplacementForm()

    return render(
        request,
        'device_replacement.html',
        {
            'title': _('Devices Replacement'),
            'form': form
        }
    )
