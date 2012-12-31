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
    status = []
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
            status.append({
                'icon': vars().get('icon', 'information.png'),
                'url': vars().get('url', reverse('dashboard')),
                'result': '%d %s' % (result, vars().get('msg', check.name))
            })

    return status


def get_current_status():
    status = execute_active_checkings()
    if type(status) is dict:
        ret = _('Error')
    elif len(status) == 0:
        ret = _('All O.K.')
    else:
        ret = _('Warning')

    return ret


@login_required
def status(request):
    """
    Status of checkings
    """
    template = 'server/status.html'
    if request.is_ajax():
        template = 'server/includes/status.html'

    status = execute_active_checkings()
    if type(status) is dict and status.get('error').get('description'):
        return render(
            request,
            'error.html',
            {
                'description': status.get('error').get('description'),
                'contentpage': status.get('error').get('contentpage')
            }
        )

    return render(
        request,
        template,
        {
            'title': _('Status'),
            'status': status,
        }
    )


def ajax_status(request):
    return HttpResponse(get_current_status(), content_type='text/plain')
