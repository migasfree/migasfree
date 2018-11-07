# -*- coding: utf-8 -*-

import json

from collections import defaultdict

from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext as _

from migasfree.server.models import Computer, Platform


def productive_computers_by_platform(user):
    total = Computer.productive.scope(user).count()
    link = '{}?_REPLACE_&status__in={}'.format(
        reverse('admin:server_computer_changelist'),
        'intended,reserved,unknown'
    )

    values = defaultdict(list)
    for item in Computer.productive.scope(user).values(
        'project__name',
        'project__id',
        'project__platform__id'
    ).annotate(
        count=Count('id')
    ).order_by('project__platform__id', '-count'):
        percent = float(item.get('count')) / total * 100
        values[item.get('project__platform__id')].append(
            {
                'name': item.get('project__name'),
                'value': item.get('count'),
                'y': float('{:.2f}'.format(percent)),
                'url': link.replace(
                    '_REPLACE_',
                    'project__id__exact={}'.format(item.get('project__id'))
                ),
            }
        )

    data = []
    for platform in Platform.objects.scope(user).all():
        if platform.id in values:
            count = sum(item['value'] for item in values[platform.id])
            percent = float(count) / total * 100
            data.append(
                {
                    'name': platform.name,
                    'value': count,
                    'y': float('{:.2f}'.format(percent)),
                    'url': link.replace(
                        '_REPLACE_',
                        'project__platform__id__exact={}'.format(platform.id)
                    ),
                    'data': values[platform.id]
                }
            )

    return {
        'title': _('Productive Computers'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('_REPLACE_&', ''),
    }


def computers_by_machine(user):
    total = Computer.objects.scope(user).count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_computer_changelist')
    )

    values = defaultdict(list)
    data = []

    count_subscribed = Computer.subscribed.scope(user).count()
    count_subscribed_virtual = Computer.subscribed.scope(user).filter(machine='V').count()
    count_subscribed_physical = Computer.subscribed.scope(user).filter(machine='P').count()
    count_unsubscribed = Computer.unsubscribed.scope(user).count()
    count_unsubscribed_virtual = Computer.unsubscribed.scope(user).filter(machine='V').count()
    count_unsubscribed_physical = Computer.unsubscribed.scope(user).filter(machine='P').count()

    if count_subscribed:
        if count_subscribed_virtual:
            values['subscribed'].append(
                {
                    'name': _('Virtual'),
                    'value': count_subscribed_virtual,
                    'y': float('{:.2f}'.format(float(count_subscribed_virtual) / total * 100)),
                    'url': link.replace(
                        '_REPLACE_',
                        'status__in=intended,reserved,unknown,available,in repair&machine__exact=V'
                    )
                }
            )

        if count_subscribed_physical:
            values['subscribed'].append(
                {
                    'name': _('Physical'),
                    'value': count_subscribed_physical,
                    'y': float('{:.2f}'.format(float(count_subscribed_physical) / total * 100)),
                    'url': link.replace(
                        '_REPLACE_',
                        'status__in=intended,reserved,unknown,available,in repair&machine__exact=P'
                    )
                }
            )

        data.append(
            {
                'name': _('Subscribed'),
                'value': count_subscribed,
                'y': float('{:.2f}'.format(float(count_subscribed) / total * 100)),
                'url': link.replace(
                    '_REPLACE_',
                    'status__in=intended,reserved,unknown,available,in repair'
                ),
                'data': values['subscribed']
            },
        )

    if count_unsubscribed:
        if count_unsubscribed_virtual:
            values['unsubscribed'].append(
                {
                    'name': _('Virtual'),
                    'value': count_unsubscribed_virtual,
                    'y': float('{:.2f}'.format(float(count_unsubscribed_virtual) / total * 100)),
                    'url': link.replace(
                        '_REPLACE_',
                        'status__in=unsubscribed&machine__exact=V'
                    )
                }
            )

        if count_unsubscribed_physical:
            values['unsubscribed'].append(
                {
                    'name': _('Physical'),
                    'value': count_unsubscribed_physical,
                    'y': float('{:.2f}'.format(float(count_unsubscribed_physical) / total * 100)),
                    'url': link.replace(
                        '_REPLACE_',
                        'status__in=unsubscribed&machine__exact=P'
                    )
                }
            )

        data.append(
            {
                'name': _('Unsubscribed'),
                'value': count_unsubscribed,
                'y': float('{:.2f}'.format(float(count_unsubscribed) / total * 100)),
                'url': link.replace(
                    '_REPLACE_',
                    'status__in=unsubscribed'
                ),
                'data': values['unsubscribed']
            }
        )

    return {
        'title': _('Computers / Machine'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('?_REPLACE_', ''),
    }


def computers_by_status(user):
    total = Computer.objects.scope(user).exclude(status='unsubscribed').count()
    link = '{}?_REPLACE_'.format(
        reverse('admin:server_computer_changelist')
    )

    values = dict()
    for item in Computer.objects.scope(user).exclude(
        status='unsubscribed'
    ).values(
        'status'
    ).annotate(
        count=Count('id')
    ).order_by('status', '-count'):
        status_name = _(dict(Computer.STATUS_CHOICES)[item.get('status')])
        percent = float(item.get('count')) / total * 100
        values[item.get('status')] = {
            'name': status_name,
            'value': item.get('count'),
            'y': float('{:.2f}'.format(percent)),
            'url': link.replace(
                '_REPLACE_',
                'status__in={}'.format(item.get('status'))
            ),
        }

    count_productive = values.get('intended', {}).get('value', 0) \
        + values.get('reserved', {}).get('value', 0) \
        + values.get('unknown', {}).get('value', 0)
    percent_productive = float(count_productive) / total * 100 if count_productive else 0
    data_productive = []
    if 'intended' in values:
        data_productive.append(values['intended'])
    if 'reserved' in values:
        data_productive.append(values['reserved'])
    if 'unknown' in values:
        data_productive.append(values['unknown'])

    count_unproductive = values.get('available', {}).get('value', 0) \
        + values.get('in repair', {}).get('value', 0)
    percent_unproductive = float(count_unproductive) / total * 100 if count_unproductive else 0
    data_unproductive = []
    if 'available' in values:
        data_unproductive.append(values['available'])
    if 'in repair' in values:
        data_unproductive.append(values['in repair'])

    data = [
        {
            'name': _('Productive'),
            'value': count_productive,
            'y': float('{:.2f}'.format(percent_productive)),
            'url': link.replace(
                '_REPLACE_',
                'status__in=intended,reserved,unknown'
            ),
            'data': data_productive,
        },
        {
            'name': _('Unproductive'),
            'value': count_unproductive,
            'y': float('{:.2f}'.format(percent_unproductive)),
            'url': link.replace(
                '_REPLACE_',
                'status__in=available,in repair'
            ),
            'data': data_unproductive,
        },
    ]

    return {
        'title': _('Subscribed Computers / Status'),
        'total': total,
        'data': json.dumps(data),
        'url': link.replace('_REPLACE_', 'status__in=intended,reserved,unknown,available,in repair'),
    }


@login_required
def computers_summary(request):
    user = request.user.userprofile

    return render(
        request,
        'computers_summary.html',
        {
            'title': _('Computers'),
            'chart_options': {
                'no_data': _('There are no data to show'),
            },
            'productive_computers_by_platform': productive_computers_by_platform(user),
            'computers_by_machine': computers_by_machine(user),
            'computers_by_status': computers_by_status(user),
        }
    )
