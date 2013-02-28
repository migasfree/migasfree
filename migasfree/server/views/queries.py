# -*- coding: utf-8 -*-

import sys

from datetime import timedelta
from datetime import datetime

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
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


def execute_query(request, parameters, form_param):
    o_query = Query.objects.get(id=parameters["id_query"])

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
            'server/query.html',
            {
                "title": o_query.name,
                "description": o_query.description,
                "titles": titles,
                "query": vl_fields,
                "filters": filters,
                'form': form_param
            }
        )
    except:
        return render(
            request,
            'error.html',
            {
                'description': "Error in field 'code' of query:",
                'contentpage': str(sys.exc_info())
            }
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
            return execute_query(request, dic_initial, {})
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

                return execute_query(request, parameters, g_form_param)
            except:
                return render(
                    request,
                    'error.html',
                    {
                        'description': "Error in field 'parameters' of query:",
                        'contentpage': str(sys.exc_info()[1])
                    }
                )

    # show parameters form
    version = get_object_or_404(UserProfile, id=request.user.id).version

    o_query = get_object_or_404(Query, id=query_id)
    dic_initial = {
        'id_query': query_id,
        'user_version': version.id
    }
    if o_query.parameters == "":
        return execute_query(request, dic_initial, {})
    else:
        try:
            # What's that, Alberto???
            def form_params():
                pass

            exec(o_query.parameters.replace("\r", ""))

            return render(
                request,
                'server/query.html',
                {
                    'form': form_params()(initial=dic_initial),
                    'title': _("Parameters for Query: %s") % o_query.name,
                }
            )
        except:
            return render(
                request,
                'error.html',
                {
                    'description': "Error in field 'parameters' of query",
                    'contentpage': str(sys.exc_info()[1])
                }
            )


@login_required
def computer_messages(request):
    template = 'server/computer_messages.html'
    if request.is_ajax():
        template = 'server/includes/computer_messages_result.html'

    t = datetime.now() - timedelta(0, MIGASFREE_SECONDS_MESSAGE_ALERT)

    result = []
    for item in Message.objects.all().order_by("-date"):
        if item.date < t:
            icon = 'messagealert.png'
        else:
            icon = 'message.png'

        try:
            last = item.computer.last_login()
            user = '%s-%s' % (last.user.name, last.user.fullname)
            lastloginid = last.id
        except:
            user = "None"
            lastloginid = 0

        result.append(
            [
                icon,
                "-",
                item.computer.id,
                item.computer.name,
                lastloginid,
                user,
                item.computer.version.name,
                item.computer.ip,
                item.date,
                item.text
            ]
        )

    return render(
        request,
        template,
        {
            "title": _("Computer Messages"),
            "query": result,
        }
    )


@login_required
def server_messages(request):
    template = 'server/server_messages.html'
    if request.is_ajax():
        template = 'server/includes/server_messages_result.html'

    result = []
    for item in MessageServer.objects.all().order_by("-date"):
        result.append(
            [
                'messageserver.png',
                "-",
                item.date,
                item.text
            ]
        )

    return render(
        request,
        template,
        {
            "title": _("Server Messages"),
            "query": result,
        }
    )
