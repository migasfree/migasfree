# -*- coding: utf-8 -*-

import sys

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.db.models import Q

from migasfree.server.models import Checking, Message


@login_required
def main(request):
    """
    dashboard of migasfree
    """

    status = []
    for obj in Checking.objects.filter(active=True):
        msg = ""
        try:
            exec(obj.code.replace("\r", ""))
            result = vars().get('result', 0)
            if result != 0:
                msg = _(vars().get('msg', obj.name))
                url = vars().get('url', reverse('bootstrap'))
                icon = vars().get('icon', 'information.png')

                status.append(
                    {
                        'icon': icon,
                        'url': url,
                        'result': '%s %s' % (str(result), msg)
                    }
                )
        except:
            return render(
                request,
                'error.html',
                {
                    'description': "Error in field 'code' of Checking:",
                    'contentpage': "%s\n%s" % (msg, str(sys.exc_info()))
                }
            )

    if len(status) == 0:
        status.append(
            {
                'icon': 'checking.png',
                'url': '#',
                'result': _('All O.K.')
            }
        )

    return render(
        request,
        'main.html',
        {
            'title': _('Status'),
            'status': status,
        }
    )
