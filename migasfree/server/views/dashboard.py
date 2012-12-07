# -*- coding: utf-8 -*-

import sys

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse

from migasfree.server.models import *
from migasfree.settings import STATIC_URL


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


@login_required
def main(request):
    """
    Status of checkings
    """
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

    if len(status) == 0:
        status.append({
            'icon': 'checking.png',
            'url': '#',
            'result': _('All O.K.')
        })

    return render(
        request,
        'main.html',
        {
            'title': _('Status'),
            'status': status,
        }
    )


def ajax_status(request):
    ret = '%s: ' % _('Status')

    status = execute_active_checkings()
    if type(status) is dict:
        ret += '<a href="%s">%s</a>' % (reverse('dashboard'), _('Error'))
    elif len(status) == 0:
        ret += '<strong>%s</strong>' % _('All O.K.')
    else:
        ret += '<a href="%s">%s</a>' % (reverse('dashboard'), _('Warning'))

    return HttpResponse(ret, content_type='text/plain')


def ajax_status_list(request):
    ret = ''
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

    if len(status) == 0:
        ret += '<li><img src="%sicons/checking.png" />%s</li>' % (
            STATIC_URL,
            _('All O.K.')
        )
    else:
        css_class = 'odd'
        for item in status:
            ret += '<li class="%s"><a href="%s"><img src="%sicons/%s" /> %s</a></li>' % (
                css_class,
                item['url'],
                STATIC_URL,
                item['icon'],
                item['result']
            )
            if css_class == 'odd':
                css_class = 'even'
            else:
                css_class = 'odd'

    return HttpResponse(ret, content_type='text/plain')
