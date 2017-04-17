# -*- coding: utf-8 -*-

import os
import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext as _

from ..api import *
from ..models import Error, Notification
from ..secure import wrap, unwrap
from ..utils import get_client_ip, uuid_validate, read_file
from .. import errmfs

# USING USERNAME AND PASSWORD ONLY (WITHOUT KEYS PAIR)
API_REGISTER = (
    "register_computer",
    "get_key_packager",
)

# USING "PACKAGER" KEYS PAIR
API_PACKAGER = (
    "upload_server_package",
    "upload_server_set",
    "create_repositories_of_packageset",
)

# USING "VERSION" KEYS
API_VERSION = (
    "upload_computer_message",
    "get_properties",
    "upload_computer_info",
    "upload_computer_faults",
    "upload_computer_hardware",
    "upload_computer_software_base_diff",
    "upload_computer_software_base",
    "upload_computer_software_history",
    "get_computer_software",
    "upload_computer_errors",
    "upload_devices_changes",
    "set_computer_tags",
    "get_computer_tags",
)


def check_tmp_path():
    if not os.path.exists(settings.MIGASFREE_TMP_DIR):
        try:
            os.makedirs(settings.MIGASFREE_TMP_DIR, 0o700)
        except OSError:
            pass  # FIXME


def wrap_command_result(filename, result):
    wrap(filename, result)
    ret = read_file(filename)
    os.remove(filename)

    return ret


def get_msg_info(text):
    slices = text.split('.')
    if len(slices) == 2:  # COMPATIBILITY WITHOUT UUID
        name, command = slices
        uuid = name
    else:  # WITH UUID
        name = '.'.join(slices[:-2])
        uuid = uuid_validate(slices[-2])
        if not uuid:
            uuid = name
        command = slices[-1]

    return command, uuid, name


@csrf_exempt
def api(request):
    # Other data on the request.FILES dictionary:
    #   filesize = len(file['content'])
    #   filetype = file['content-type']

    check_tmp_path()

    if request.method != 'POST':
        return HttpResponse(
            return_message(
                'unexpected_get_method',
                errmfs.error(errmfs.GET_METHOD_NOT_ALLOWED)
            ),
            content_type='text/plain'
        )

    msg = request.FILES.get('message')
    filename = os.path.join(settings.MIGASFREE_TMP_DIR, msg.name)
    filename_return = "{}.return".format(filename)

    command, uuid, name = get_msg_info(msg.name)
    computer = get_computer(name, uuid)

    if computer and computer.status == 'unsubscribed':
        Error.objects.create(
            computer,
            computer.project,
            "{} - {} - {}".format(
                get_client_ip(request),
                command,
                errmfs.error_info(errmfs.UNSUBSCRIBED_COMPUTER)
            )
        )
        ret = return_message(
            command,
            errmfs.error(errmfs.UNSUBSCRIBED_COMPUTER)
        )
        return HttpResponse(
            wrap_command_result(filename_return, ret),
            content_type='text/plain'
        )

    if computer and computer.status == 'available' \
            and command == 'upload_computer_info':
        Notification.objects.create(
            _('Computer [%s] with available status, has been synchronized')
            % '<a href="{}">{}</a>'.format(
                reverse('admin:server_computer_change', args=(computer.id,)),
                computer
            )
        )

    # COMPUTERS
    if command in API_VERSION:  # IF COMMAND IS BY VERSION
        if computer:
            save_request_file(msg, filename)

            # UNWRAP AND EXECUTE COMMAND
            data = unwrap(filename, computer.project.name)
            if 'errmfs' in data:
                ret = return_message(command, data)

                if data["errmfs"]["code"] == errmfs.INVALID_SIGNATURE:
                    Error.objects.create(
                        computer,
                        computer.project,
                        "{} - {} - {}".format(
                            get_client_ip(request),
                            command,
                            errmfs.error_info(errmfs.INVALID_SIGNATURE)
                        )
                    )
            else:
                ret = eval(command)(request, name, uuid, computer, data)

            os.remove(filename)
        else:
            ret = return_message(
                command,
                errmfs.error(errmfs.COMPUTER_NOT_FOUND)
            )

        return HttpResponse(
            wrap_command_result(filename_return, ret),
            content_type='text/plain'
        )

    # REGISTERS
    # COMMAND NOT USE KEYS PAIR, ONLY USERNAME AND PASSWORD
    elif command in API_REGISTER:
        save_request_file(msg, filename)

        with open(filename, 'rb') as f:
            data = json.load(f)[command]

        try:
            ret = eval(command)(request, name, uuid, computer, data)
        except:
            ret = return_message(command, errmfs.error(errmfs.GENERIC))

        os.remove(filename)

        return HttpResponse(json.dumps(ret), content_type='text/plain')

    # PACKAGER
    elif command in API_PACKAGER:
        save_request_file(msg, filename)

        # UNWRAP AND EXECUTE COMMAND
        data = unwrap(filename, "migasfree-packager")
        if 'errmfs' in data:
            ret = data
        else:
            ret = eval(command)(request, name, uuid, computer, data[command])

        os.remove(filename)

        return HttpResponse(
            wrap_command_result(filename_return, ret),
            content_type='text/plain'
        )

    else:
        return HttpResponse(
            return_message(command, errmfs.error(errmfs.COMMAND_NOT_FOUND)),
            content_type='text/plain'
        )
