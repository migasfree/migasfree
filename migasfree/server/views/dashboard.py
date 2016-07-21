# -*- coding: utf-8 -*-

import sys

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.db.models import Q  # backwards compatibility

from ..models import *


def execute_active_checkings(request):
    """
    Returns active checkings results, as a list
    If an error occurs, returns a dictionary with execution error information
    If no results, returns empty list

    request parameter maybe used in exec code call (not unused!!!)
    """
    checkings = []
    for check in Checking.objects.filter(active=True).order_by('alert'):
        try:
            exec(check.code.replace("\r", ""))
        except:
            return {
                'error': {
                    'description': _("Error in field 'code' of Checking: %s") % check.name,
                    'contentpage': '{}\n{}'.format(check.code, sys.exc_info())
                }
            }

        result = vars().get('result', 0)
        if result > 0:
            checkings.append({
                'badge': result,
                'alert': vars().get('alert', 'info'),
                'target': vars().get('target', 'computer'),
                'url': vars().get('url', reverse('bootstrap')),
                'msg': vars().get('msg', check.name),
            })

        vars().clear()

    return checkings


@permission_required('server.change_checking', raise_exception=True)
@login_required
def alerts(request):
    """
    Status of checkings
    """
    checkings = execute_active_checkings(request)
    if isinstance(checkings, dict) and checkings.get('error').get('description'):
        return render(
            request,
            'error.html',
            {
                'description': checkings.get('error').get('description'),
                'contentpage': checkings.get('error').get('contentpage')
            }
        )

    return render(
        request,
        'includes/alerts.html',
        {
            'title': _('Status'),
            'alerts': checkings,
            'badge': sum(row['badge'] for row in checkings),
        }
    )
