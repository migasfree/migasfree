# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.utils.translation import ugettext as _

from .tasks import checkings


@permission_required('server.change_userprofile', raise_exception=True)
@login_required
def alerts(request):
    """
    Checkings status
    """
    results = checkings(request.user.id)

    return render(
        request,
        'includes/alerts.html',
        {
            'title': _('Alerts'),
            'alerts': results,
            'result': sum(row['result'] for row in results),
        }
    )
