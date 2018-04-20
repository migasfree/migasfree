# -*- coding: utf-8 -*-

import json

from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext as _

from migasfree.server.models import Device, DeviceModel


def devices_by_connection():
    total = Device.objects.count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_device_changelist')
    )

    data = []
    for item in Device.objects.values(
        'connection__name',
        'connection__id',
    ).annotate(
        count=Count('id')
    ).order_by('-count'):
        percent = float(item['count']) / total * 100
        data.append({
            'name': item['connection__name'],
            'value': item['count'],
            'y': float('{:.2f}'.format(percent)),
            'url': link.replace(
                '_REPLACE_',
                'connection__id__exact={}'.format(item['connection__id'])
            ),
        })

    return {
        'title': _('Devices / Connection'),
        'total': total,
        'data': json.dumps(data),
    }


def devices_by_model():
    total = Device.objects.count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_device_changelist')
    )

    data = []
    for item in Device.objects.values(
        'model__name',
        'model__id',
    ).annotate(
        count=Count('id')
    ).order_by('-count'):
        percent = float(item['count']) / total * 100
        data.append({
            'name': item['model__name'],
            'value': item['count'],
            'y': float('{:.2f}'.format(percent)),
            'url': link.replace(
                '_REPLACE_',
                'model__id__exact={}'.format(item['model__id'])
            ),
        })

    return {
        'title': _('Devices / Model'),
        'total': total,
        'data': json.dumps(data),
    }


def devices_by_manufacturer():
    total = Device.objects.count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_device_changelist')
    )

    data = []
    for item in Device.objects.values(
        'model__manufacturer__name',
        'model__manufacturer__id',
    ).annotate(
        count=Count('id')
    ).order_by('-count'):
        percent = float(item['count']) / total * 100
        data.append({
            'name': item['model__manufacturer__name'],
            'value': item['count'],
            'y': float('{:.2f}'.format(percent)),
            'url': link.replace(
                '_REPLACE_',
                'model__manufacturer__id__exact={}'.format(item['model__manufacturer__id'])
            ),
        })

    return {
        'title': _('Devices / Manufacturer'),
        'total': total,
        'data': json.dumps(data),
    }


def models_by_manufacturer():
    total = DeviceModel.objects.count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_devicemodel_changelist')
    )

    data = []
    for item in DeviceModel.objects.values(
        'manufacturer__name',
        'manufacturer__id',
    ).annotate(
        count=Count('id')
    ).order_by('-count'):
        percent = float(item['count']) / total * 100
        data.append({
            'name': item['manufacturer__name'],
            'value': item['count'],
            'y': float('{:.2f}'.format(percent)),
            'url': link.replace(
                '_REPLACE_',
                'manufacturer__id__exact={}'.format(item['manufacturer__id'])
            ),
        })

    return {
        'title': _('Models / Manufacturer'),
        'total': total,
        'data': json.dumps(data),
    }


@login_required
def devices_summary(request):
    return render(
        request,
        'devices_summary.html',
        {
            'title': _('Devices Summary'),
            'chart_options': {
                'no_data': _('There are no data to show'),
                'reset_zoom': _('Reset Zoom'),
            },
            'devices_by_connection': devices_by_connection(),
            'devices_by_model': devices_by_model(),
            'devices_by_manufacturer': devices_by_manufacturer(),
            'models_by_manufacturer': models_by_manufacturer(),
        }
    )
