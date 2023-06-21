# -*- coding: utf-8 -*-

import os
import time
import json
import ssl
import tempfile
import shutil
import hashlib

from django.conf import settings
from django.http import HttpResponse, JsonResponse, Http404, StreamingHttpResponse

from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext as _

from rest_framework.decorators import permission_classes
from rest_framework import permissions, views
from rest_framework.response import Response
from rest_framework import status

from urllib.error import URLError, HTTPError
from urllib.request import urlopen, urlretrieve, urlcleanup
from wsgiref.util import FileWrapper

from ..models import Platform, Project, Deployment, ExternalSource, Notification
from ..api import get_computer
from ..utils import uuid_validate, get_client_ip
from ..secure import gpg_get_key


def get_projects(request):
    result = []
    for plat in Platform.objects.all():
        element = {
            "platform": plat.name,
            "projects": []
        }
        for prj in Project.objects.filter(platform=plat):
            element["projects"].append({"name": prj.name})

        result.append(element)

    return JsonResponse(result, safe=False)


def get_computer_info(request, uuid=None):
    if uuid:
        _uuid = uuid_validate(uuid)
    else:
        _uuid = uuid_validate(request.GET.get('uuid', ''))
    _name = request.GET.get('name', '')
    if _uuid == "":
        _uuid = _name

    computer = get_computer(_name, _uuid)
    if not computer:
        raise Http404

    result = {
        'id': computer.id,
        'uuid': computer.uuid,
        'name': computer.__str__(),
        'helpdesk': settings.MIGASFREE_HELP_DESK,
        'server': request.META.get('HTTP_HOST'),
        'tags': ["{}-{}".format(tag.property_att.prefix, tag.value) for tag in computer.tags.all()],
        'available_tags': {},
    }
    result["search"] = result[settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0]]

    for deploy in Deployment.objects.filter(
        project=computer.project, enabled=True
    ):
        for tag in deploy.included_attributes.filter(
            property_att__sort='server', property_att__enabled=True
        ):
            if tag.property_att.name not in result["available_tags"]:
                result["available_tags"][tag.property_att.name] = []

            value = "{}-{}".format(tag.property_att.prefix, tag.value)
            if value not in result["available_tags"][tag.property_att.name]:
                result["available_tags"][tag.property_att.name].append(value)

    return JsonResponse(result)


def computer_label(request, uuid=None):
    """
    To Print a Computer Label
    """
    if not uuid:
        uuid = request.GET.get('uuid', '')

    computer_info = json.loads(get_computer_info(request, uuid).content)

    return render(
        request,
        'computer_label.html',
        computer_info
    )


def get_key_repositories(request):
    """
    Returns the repositories public key
    """
    return HttpResponse(
        gpg_get_key("migasfree-repository"),
        content_type="text/plain"
    )


def add_notification_get_source_file(error, deployment, resource, remote, from_):
    Notification.objects.create(
        _("Deployment (external source) [%s]: [%s] resource: [%s], remote file: [%s], from [%s].") % (
            '<a href="{}">{}</a>'.format(
                reverse('admin:server_externalsource_change', args=(deployment.id,)),
                deployment
            ),
            error,
            resource,
            remote,
            from_
        )
    )


def external_downloads(url, local_file):
    temp_file = os.path.join(
        settings.MIGASFREE_PUBLIC_DIR,
        '.external_downloads',
        hashlib.md5(local_file.encode('utf-8')).hexdigest()
    )

    if not os.path.exists(temp_file):
        os.makedirs(os.path.dirname(temp_file), exist_ok=True)
        urlcleanup()
        urlretrieve(url, temp_file)
        shutil.move(temp_file, local_file)


def get_source_file(request):

    def read_remote_chunks(local_file, remote, chunk_size=8192):
        _, tmp = tempfile.mkstemp()
        with open(tmp, 'wb') as tmp_file:
            while True:
                data = remote.read(chunk_size)
                if not data:
                    break

                yield data
                tmp_file.write(data)
                tmp_file.flush()

            os.fsync(tmp_file.fileno())
        shutil.move(tmp, local_file)

    source = None

    _path = request.get_full_path()
    project_name = _path.split('/')[2]
    source_name = _path.split('/')[4]
    resource = _path.split('/src/{}/EXTERNAL/{}/'.format(project_name, source_name))[1]

    _file_local = os.path.join(settings.MIGASFREE_PUBLIC_DIR, _path.split('/src/')[1])

    # FIXME PMS dependency
    if not (_file_local.endswith('.deb') or _file_local.endswith('.rpm')):  # is a metadata file
        source = ExternalSource.objects.get(project__name=project_name, name=source_name)

        if not source.frozen:
            # expired metadata
            if os.path.exists(_file_local) and (
                source.expire <= 0 or
                (time.time() - os.stat(_file_local).st_mtime) / (60 * source.expire) > 1
            ):
                os.remove(_file_local)

    if not os.path.exists(_file_local):
        if not os.path.exists(os.path.dirname(_file_local)):
            os.makedirs(os.path.dirname(_file_local))

        if not source:
            source = ExternalSource.objects.get(project__name=project_name, name=source_name)

        url = '{}/{}'.format(source.base_url, resource)

        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            remote_file = urlopen(url, context=ctx)
            response = StreamingHttpResponse(read_remote_chunks(_file_local, remote_file))
            response['Content-Type'] = 'application/octet-stream'
            return response
        except HTTPError as e:
            add_notification_get_source_file(
                "HTTP Error: {}".format(e.code),
                source, _path, url,
                get_client_ip(request)
            )
            return HttpResponse(
                'HTTP Error: {} {}'.format(e.code, url),
                status=e.code
            )
        except URLError as e:
            add_notification_get_source_file(
                "URL Error: {}".format(e.reason),
                source, _path, url,
                get_client_ip(request)
            )
            return HttpResponse(
                'URL Error: {} {}'.format(e.reason, url),
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        if not os.path.isfile(_file_local):
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)
        else:
            response = HttpResponse(FileWrapper(open(_file_local, 'rb')), content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename={}'.format(os.path.basename(_file_local))
            response['Content-Length'] = os.path.getsize(_file_local)
            return response


@permission_classes((permissions.AllowAny,))
class RepositoriesUrlTemplateView(views.APIView):
    def post(self, request, format=None):
        """
        Returns the repositories URL template
        (compatibility for migasfree-client <= 4.16)
        """
        protocol = 'https' if request.is_secure() else 'http'

        return Response(
            '{}://{{server}}{}{{project}}/{}'.format(
                protocol,
                settings.MEDIA_URL,
                Project.REPOSITORY_TRAILING_PATH
            ),
            content_type='text/plain'
        )


@permission_classes((permissions.AllowAny,))
class ServerInfoView(views.APIView):
    def post(self, request, format=None):
        """
        Returns server info
        """
        from ... import __version__, __author__, __contact__, __homepage__

        info = {
            'version': __version__,
            'author': __author__,
            'contact': __contact__,
            'homepage': __homepage__,
        }

        return Response(info)
