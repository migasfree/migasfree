# -*- coding: utf-8 -*-

import sys
import inspect

from datetime import datetime, timedelta

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django import forms
from django.conf import settings

from ..models import *


def option_description(field, value):
    try:
        return field.split(
            '<option value="%s">' % value
        )[1].split("</option>")[0]
    except:
        return value


def execute_query(request, parameters, form_param):
    o_query = get_object_or_404(Query, id=parameters.get('id_query', ''))

    try:
        exec(o_query.code.replace("\r", ""))
        # after exec, new available variables are: query, fields, titles

        if 'fields' not in vars():
            fields = []
            for key in query.values()[0].iterkeys():
                fields.append(key)

        if 'titles' not in vars():
            titles = fields

        results = []

        for obj in query:
            cols = []
            for field in fields:
                try:
                    value = getattr(obj, field)

                    # to allow calls to model methods (as link)
                    if obj._deferred and inspect.ismethod(value):
                        meta_model = obj._meta.proxy_for_model.objects.get(
                            pk=obj.id
                        )
                        cols.append(getattr(meta_model, field)())
                    else:
                        cols.append(value)
                except AttributeError:
                    cols.append(eval("obj.%s" % field))

            results.append(cols)

        filters = []
        for x in form_param:
            if not (x.name == "id_query" or x.name == "user_version"):
                filters.append('%s: %s' % (
                    x.label,
                    str(parameters["%s_display" % x.name])
                ))

        return render(
            request,
            'query.html',
            {
                "title": o_query.name,
                "description": o_query.description,
                "titles": titles,
                "query": results,
                "filters": filters,
                'form': form_param
            }
        )
    except:
        return render(
            request,
            'error.html',
            {
                'description': _("Error in field 'code' of query:"),
                'contentpage': o_query.code + '\n' + str(sys.exc_info())
            }
        )


@login_required
def query(request, query_id):
    if request.method == 'POST':
        parameters = {}
        for p in request.POST:
            parameters[p] = request.POST.get(p)

        query = get_object_or_404(Query, id=request.POST.get('id_query', ''))
        dic_initial = {
            'id_query': request.POST.get('id_query', ''),
            'user_version': request.user.userprofile.version_id
        }
        dic_initial.update(parameters)
        if query.parameters == "":
            return execute_query(request, dic_initial, {})

        try:
            def form_params():
                pass

            exec(query.parameters.replace("\r", ""))
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
                    'description': _("Error in field 'parameters' of query:"),
                    'contentpage': str(sys.exc_info()[1])
                }
            )

    # show parameters form
    version = get_object_or_404(UserProfile, id=request.user.id).version
    if not version:
        # The user not have a version. We assign to user the first version found
        version = Version.objects.all().order_by("id")[0]
        user = UserProfile.objects.get(id=request.user.id)
        user.update_version(version)

    query = get_object_or_404(Query, id=query_id)
    dic_initial = {
        'id_query': query_id,
        'user_version': version.id
    }
    if query.parameters == "":
        return execute_query(request, dic_initial, {})

    try:
        def form_params():
            pass

        exec(query.parameters.replace("\r", ""))

        return render(
            request,
            'query.html',
            {
                'form': form_params()(initial=dic_initial),
                'title': query.name,
            }
        )
    except:
        return render(
            request,
            'error.html',
            {
                'description': _("Error in field 'parameters' of query:"),
                'contentpage': str(sys.exc_info()[1])
            }
        )


@login_required
def computer_messages(request):
    template = 'computer_messages.html'
    if request.is_ajax():
        template = 'includes/computer_messages_result.html'

    t = datetime.now() - timedelta(0, settings.MIGASFREE_SECONDS_MESSAGE_ALERT)

    result = []
    for item in Message.objects.all().order_by("-date"):
        if item.date < t:
            icon = 'warning'
        else:
            icon = 'refresh fa-spin'

        try:
            login = Login.objects.get(computer=item.computer)
            user = '%s-%s' % (login.user.name, login.user.fullname)
            loginid = login.id
        except:
            user = "None"
            loginid = 0

        result.append(
            [
                icon,
                "-",
                item.computer.id,
                item.computer.__str__(),
                loginid,
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
    template = 'server_messages.html'
    if request.is_ajax():
        template = 'includes/server_messages_result.html'

    result = []
    for item in MessageServer.objects.all().order_by("-date"):
        result.append(
            [
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
