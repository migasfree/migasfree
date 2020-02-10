# -*- coding: utf-8 -*-

import sys
import inspect

from datetime import datetime, timedelta
from six import iteritems, iterkeys

from django import forms  # for execute_query function
from django.db.models import Q  # for execute_query function
from django.db.models import DEFERRED
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _

from ..models import Query, Message


def execute_query(request, parameters, form_param=None):
    o_query = get_object_or_404(Query, id=parameters.get('id_query'))

    try:
        namespace = {'Q': Q, 'parameters': parameters, 'request': request}
        exec(o_query.code.replace("\r", ""), namespace)

        # after exec, new available variables are: query, fields, titles
        query = namespace.get('query', [])
        fields = namespace.get('fields', [])
        titles = namespace.get('titles', [])

        if not fields:
            for key in iterkeys(query.values()[0]):
                fields.append(key)

        if not titles:
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
                    if DEFERRED and inspect.ismethod(value):
                        cols.append(getattr(obj, field)())
                    else:
                        cols.append(value)

            results.append(cols)

        filters = []
        if form_param:
            for item in form_param:
                if item.name not in ['id_query']:
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

    default_parameters = {
        'id_query': query_id,
    }

    if request.method == 'POST':
        default_parameters.update(dict(iteritems(request.POST)))

    if not query.parameters:
        return execute_query(request, default_parameters)

    try:
        # this function will be override after exec query.parameters
        # only declared to avoid unresolved reference
        def form_params(request):
            pass

        namespace = {'forms': forms}
        exec(query.parameters.replace("\r", ""), namespace)
        form_params = namespace['form_params']
        form = form_params(request)(initial=default_parameters)

        if request.method == 'POST':
            for item in form:
                default_parameters['{}_display'.format(item.name)] = strip_tags(
                    str(item)
                )

            return execute_query(request, default_parameters, form)

        return render(
            request,
            'query.html',
            {
                'form': form,
                'title': query.name,
                'description': query.description,
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
        seconds=settings.MIGASFREE_SECONDS_MESSAGE_ALERT
    )

    data = Message.objects.raw("""
        SELECT server_message.id, server_message.computer_id,
        server_message.text, server_message.updated_at,
        server_computer.name AS computer_name, server_computer.ip_address,
        server_user.name, server_user.fullname, server_user.id AS user_id,
        server_project.name AS project_name
        FROM server_message INNER JOIN server_computer
            ON (server_message.computer_id = server_computer.id)
        INNER JOIN server_project
            ON (server_computer.project_id = server_project.id)
        INNER JOIN server_user
            ON (server_computer.sync_user_id = server_user.id)
        ORDER BY server_message.updated_at DESC
    """)

    result = []
    for item in data:
        result.append(
            {
                'delayed': True if item.updated_at < delayed_time else False,
                'computer_id': item.computer_id,
                'computer_name': item.computer_name,
                'user_id': item.user_id,
                'user_name': item.name,
                'user_fullname': item.fullname,
                'project': item.project_name,
                'ip_address': item.ip_address,
                'date': item.updated_at,
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
