# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.db.models import Q

from migasfree.server.models import *


@login_required
def hardware(request, param):
    qry = HwNode.objects.filter(Q(id=param) | Q(parent=param))
    if qry.count > 0:
        computer = qry[0].computer

    return render(
        request,
        'hardware.html',
        {
            "title": computer.name,
            "computer": computer,
            "description": _("Hardware Information"),
            "query": qry,
        }
    )


@login_required
def hardware_resume(request, param):
    qry = HwNode.objects.filter(Q(computer__id=param)).order_by("id")
    if qry.count > 0:
        computer = qry[0].computer

    return render(
        request,
        'hardware_resume.html',
        {
            "title": computer.name,
            "computer": computer,
            "description": _("Hardware Information"),
            "query": qry,
        }
    )
