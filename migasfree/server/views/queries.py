# -*- coding: utf-8 -*-

import sys
import inspect

from datetime import datetime, timedelta

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q  # for execute_query function
from django import forms  # for execute_query function
from django.conf import settings

from ..models import *


def option_description(field, value):
    try:
        return field.split(
            '<option value="{}">'.format(value)
        )[1].split("</option>")[0]
    except:
        return value


def execute_query(request, parameters, form_param=None):
    o_query = get_object_or_404(Query, id=parameters.get('id_query'))

    try:
        exec(o_query.code.replace("\r", ""))
        # after exec, new available variables are: query, fields, titles

        if 'fields' not in locals():
            fields = []
            for key in query.values()[0].iterkeys():
                fields.append(key)

        if 'titles' not in locals():
            titles = fields

        results = []
        for obj in query:
            cols = []
            for field in fields:
                try:
                    value = getattr(obj, field)
                except AttributeError:
                    cols.append(eval('obj.{}'.format(field)))
                else:
                    # to allow calls to model methods (as link)
                    if obj._deferred and inspect.ismethod(value):
                        meta_model = obj._meta.proxy_for_model.objects.get(
                            pk=obj.id
                        )
                        cols.append(getattr(meta_model, field)())
                    else:
                        cols.append(value)

            results.append(cols)

        filters = []
        for item in form_param:
            if item.name not in ['id_query', 'user_version']:
                filters.append('{}: {}'.format(
                    item.label,
                    parameters['{}_display'.format(item.name)]
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
def get_query(request, query_id):
    query = get_object_or_404(Query, id=query_id)

    version = get_object_or_404(UserProfile, id=request.user.id).version
    if not version:
        # The user does not have a version
        # We assign to user the first version found
        version = Version.objects.all().order_by("id")[0]
        user = UserProfile.objects.get(id=request.user.id)
        user.update_version(version)

    default_parameters = {
        'id_query': query_id,
        'user_version': version.id
    }

    if request.method == 'POST':
        default_parameters.update(dict(request.POST.iteritems()))

    if not query.parameters:
        return execute_query(request, default_parameters)

    try:
        # this function will be override after exec query.parameters
        # only declared to avoid unresolved reference
        def form_params():
            pass

        exec(query.parameters.replace("\r", ""))
        form = form_params()(initial=default_parameters)

        if request.method == 'POST':
            for item in form:
                default_parameters['{}_display'.format(item.name)] = option_description(
                    str(item), default_parameters[item.name]
                )

            return execute_query(request, default_parameters, form)

        return render(
            request,
            'query.html',
            {
                'form': form,
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
    delayed_time = datetime.now() - timedelta(
        0, settings.MIGASFREE_SECONDS_MESSAGE_ALERT
    )

    data = Message.objects.raw("""
        SELECT server_message.id, server_message.computer_id,
        server_message.text, server_message.date,
        server_computer.name AS computer_name, server_computer.ip,
        server_user.name, server_user.fullname,
        server_version.name AS version_name,
        server_login.id AS login_id
        FROM server_message INNER JOIN server_computer
            ON (server_message.computer_id = server_computer.id)
        INNER JOIN server_login
            ON (server_computer.id = server_login.computer_id)
        INNER JOIN server_version
            ON (server_computer.version_id = server_version.id)
        INNER JOIN server_user
            ON (server_login.user_id = server_user.id)
        ORDER BY server_message.date DESC
    """)

    result = []
    for item in data:
        result.append(
            {
                'delayed': True if item.date < delayed_time else False,
                'computer_id': item.computer_id,
                'computer_name': item.computer_name,
                'login_id': item.login_id,
                'user_name': item.name,
                'user_fullname': item.fullname,
                'version': item.version_name,
                'ip': item.ip,
                'date': str(item.date),
                'text': item.text
            }
        )

    template = 'computer_messages.html'
    if request.is_ajax():
        template = 'includes/computer_messages_result.html'

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
            {
                'date': item.date,
                'text': item.text
            }
        )

    return render(
        request,
        template,
        {
            "title": _("Server Messages"),
            "query": result,
        }
    )
