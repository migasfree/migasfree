# -*- coding: utf-8 -*-

import sys

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse

from migasfree.server.models import *


def execute_active_checkings():
    """
    Returns active checkings results, as a list
    If an error occurs, returns a dictionary with execution error information
    If no results, returns empty list
    """
    alerts = []
    for check in Checking.objects.filter(active=True):
        try:
            exec(check.code.replace("\r", ""))
        except:
            return {'error': {
                'description': "Error in field 'code' of Checking: %s"
                    % check.name,
                'contentpage': '%s\n%s' % (check.code, str(sys.exc_info()))
            }}

        result = vars().get('result', 0)
        if result > 0:
            alerts.append({
                'badge': result,
                'alert': vars().get('alert', 'info'),
                'target': vars().get('target', 'computer'),
                'url': vars().get('url', reverse('bootstrap')),
                'msg': vars().get('msg', check.name),
            })

    return alerts


@login_required
def alerts(request):
    """
    Status of checkings
    """
    template = 'includes/alerts.html'

    alerts = execute_active_checkings()
    if type(alerts) is dict and alerts.get('error').get('description'):
        return render(
            request,
            'error.html',
            {
                'description': alerts.get('error').get('description'),
                'contentpage': alerts.get('error').get('contentpage')
            }
        )

    return render(
        request,
        template,
        {
            'title': _('Status'),
            'alerts': alerts,
            'badge': sum(row['badge'] for row in alerts),
        }
    )
