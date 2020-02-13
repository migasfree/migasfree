# -*- coding: utf-8 -*-

import json

from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext as _

from ...server.models import ClientAttribute, ServerAttribute


def attribute_by_property(user):
    total = ClientAttribute.objects.scope(user).count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_clientattribute_changelist')
    )

    data = []
    for item in ClientAttribute.objects.scope(user).values(
        'property_att__id', 'property_att__name'
    ).annotate(
        count=Count('property_att__id')
    ).order_by('-count'):
        percent = float(item.get('count')) / total * 100
        data.append({
            'name': item.get('property_att__name'),
            'value': item.get('count'),
            'y': float('{:.2f}'.format(percent)),
            'url': link.replace(
                '_REPLACE_',
                'Attribute={}'.format(item.get('property_att__id'))
            ),
        })

    return {
        'title': _('Attributes / Formula'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('?_REPLACE_', ''),
    }


def tag_by_category(user):
    total = ServerAttribute.objects.scope(user).count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_serverattribute_changelist')
    )

    data = []
    for item in ServerAttribute.objects.scope(user).values(
        'property_att__id', 'property_att__name'
    ).annotate(
        count=Count('property_att__id')
    ).order_by('-count'):
        percent = float(item.get('count')) / total * 100
        data.append({
            'name': item.get('property_att__name'),
            'value': item.get('count'),
            'y': float('{:.2f}'.format(percent)),
            'url': link.replace(
                '_REPLACE_',
                'Tag={}'.format(item.get('property_att__id'))
            ),
        })

    return {
        'title': _('Tags / Tag Category'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('?_REPLACE_', ''),
    }


@login_required
def attributes_summary(request):
    user = request.user.userprofile

    return render(
        request,
        'attributes_summary.html',
        {
            'title': _('Attributes'),
            'chart_options': {
                'no_data': _('There are no data to show'),
            },
            'attribute_by_property': attribute_by_property(user),
            'opts': ClientAttribute._meta,
        }
    )


@login_required
def tags_summary(request):
    user = request.user.userprofile

    return render(
        request,
        'tags_summary.html',
        {
            'title': _('Tags'),
            'chart_options': {
                'no_data': _('There are no data to show'),
            },
            'tag_by_category': tag_by_category(user),
            'opts': ServerAttribute._meta,
        }
    )
