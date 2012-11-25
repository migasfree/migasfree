# -*- coding: utf-8 -*-

import sys

from datetime import timedelta
from datetime import datetime

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django import forms

from migasfree.settings import MIGASFREE_SECONDS_MESSAGE_ALERT
from migasfree.server.models import *


def option_description(field, value):
    try:
        return field.split(
            '<option value="%s">' % value
        )[1].split("</option>")[0]
    except:
        return value


@login_required
def query_selection(request):
    """
    Queries Menu of migasfree
    """

    qry = Query.objects.all().order_by("-id")
    vl_fields = []
    for e in qry:
        vl_fields.append([e.id, e.name])

    return render(
        request,
        'query_selection.html',
        {
            "title": _("Queries Menu"),
            "query": vl_fields,
        }
    )


def query2(request, parameters, form_param):
    o_query = Query.objects.get(id=parameters["id_query"])

    # execute query
    try:
        exec(o_query.code.replace("\r", ""))

        if 'fields' not in vars():
            fields = []
            for key in query.values()[0].iterkeys():
                fields.append(key)

        if 'titles' not in vars():
            titles = fields

        vl_fields = []

        for o in query:
            o = o  # for pylint
            cols = []
            for f in fields:
                cols.append(eval("o.%s" % f))
            vl_fields.append(cols)

        filters = []
        for x in form_param:
            if not (x.name == "id_query" or x.name == "user_version"):
                filters.append('%s: %s' % (
                    str(x.label),
                    parameters["%s_display" % x.name]
                ))

        return render(
            request,
            'query.html',
            {
                "title": o_query.name,
                "description": o_query.description,
                "titles": titles,
                "query": vl_fields,
                "filters": filters,
                "row_count": query.count(),
            }
        )
    except:
        return HttpResponse(
            "Error in field 'code' of query:\n" + str(sys.exc_info()),
            mimetype="text/plain"
        )


@login_required
def query(request, query_id):
    if request.method == 'POST':
        parameters = {}
        for p in request.POST:
            parameters[p] = request.POST.get(p)

        o_query = Query.objects.get(id=request.POST.get('id_query', ''))
        dic_initial = {
            'id_query': request.POST.get('id_query', ''),
            'user_version': UserProfile.objects.get(
                id=request.user.id
            ).version.id
        }
        if o_query.parameters == "":
            return query2(request, dic_initial, {})
        else:
            try:
                def form_params():
                    pass

                exec(o_query.parameters.replace("\r", ""))
                g_form_param = form_params()(initial=dic_initial)

                for x in g_form_param:
                    parameters[x.name + "_display"] = option_description(
                        str(x), parameters[x.name]
                    )

                return query2(request, parameters, g_form_param)
            except:
                return HttpResponse(
                    "Error in field 'parameters' of query:\n"
                        + str(sys.exc_info()[1]),
                    mimetype="text/plain"
                )

    # show parameters form
    try:
        version = UserProfile.objects.get(id=request.user.id).version
    except:
        return HttpResponse(
            'No version to find info.',
            mimetype="text/plain"
        )  # FIXME

    o_query = Query.objects.get(id=query_id)
    dic_initial = {
        'id_query': query_id,
        'user_version': version.id
    }
    if o_query.parameters == "":
        return query2(request, dic_initial, {})
    else:
        try:
            def form_params():
                pass

            exec(o_query.parameters.replace("\r", ""))
            g_form_param = form_params()(initial=dic_initial)

            return render(
                request,
                'parameters.html',
                {
                    'form': g_form_param,
                    'title': _("Parameters for Query: %s") % o_query.name,
                }
            )
        except:
            return HttpResponse(
                "Error in field 'parameters' of query:\n"
                    + str(sys.exc_info()[1]),
                mimetype="text/plain"
            )


@login_required
def query_message(request):
    vl_fields = []

    q = Message.objects.all().order_by("-date")
    t = datetime.now() - timedelta(0, MIGASFREE_SECONDS_MESSAGE_ALERT)

    for e in q:
        if e.date < t:
            icon = 'computer_alert.png'
        else:
            icon = 'computer.png'

        try:
            last = e.computer.last_login()
            user = '%s-%s' % (last.user.name, last.user.fullname)
        except:
            user = "None"

        vl_fields.append(
            [
                icon,
                "-",
                e.computer.id,
                e.computer.name,
                last.id,
                user,
                e.computer.version.name,
                e.computer.ip,
                e.date,
                e.text
            ]
        )

    return render(
        request,
        'message.html',
        {
            "title": _("Computer Messages"),
            "query": vl_fields,
        }
    )


@login_required
def query_message_server(request):
    vl_fields = []

    q = MessageServer.objects.all().order_by("-date")

    for e in q:
        icon = 'spinner.gif'

        vl_fields.append(
            [
                icon,
                "-",
                e.date,
                e.text
            ]
        )

    return render(
        request,
        'messageserver.html',
        {
            "title": _("Server Messages"),
            "query": vl_fields,
        }
    )
