# -*- coding: utf-8 -*-

import os
import json

from datetime import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from ..models import Error
from ..api import *
from ..errmfs import *
from ..security import *
from ..functions import get_client_ip, uuid_validate


@csrf_exempt
def api(request):
    # Other data on the request.FILES dictionary:
    #   filesize = len(file['content'])
    #   filetype = file['content-type']

    if request.method != 'POST':
        return HttpResponse(
            return_message(
                command,
                errmfs.error(errmfs.GET_METHOD_NOT_ALLOWED)
            ),
            content_type='text/plain'
        )

    msg = request.FILES.get('message')
    filename = os.path.join(settings.MIGASFREE_TMP_DIR, msg.name)
    filename_return = "%s.return" % filename

    lst_msg = msg.name.split('.')
    if len(lst_msg) == 2:  # COMPATIBILITY WITHOUT UUID
        name, command = lst_msg
        uuid = name
    else:  # WITH UUID
        name = ".".join(lst_msg[:-2])
        uuid = uuid_validate(lst_msg[-2])
        if uuid == "":
            uuid = name
        command = lst_msg[-1]

    o_computer = get_computer(name, uuid)

    if not os.path.exists(settings.MIGASFREE_TMP_DIR):
        try:
            os.makedirs(settings.MIGASFREE_TMP_DIR, 0o700)
        except:
            pass  # FIXME

    # USING USERNAME AND PASSWORD ONLY (WITHOUT KEYS PAIR)
    cmd_register = (
        "register_computer",
        "get_key_packager"
    )

    # USING "PACKAGER" KEYS PAIR
    cmd_packager = (
        "upload_server_package",
        "upload_server_set",
        "create_repositories_of_packageset"
    )

    # USING "VERSION" KEYS
    cmd_version = (
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
        "get_computer_tags"
    )

    # COMPUTERS
    if command in cmd_version:  # IF COMMAND IS BY VERSION
        if o_computer:
            version = o_computer.version.name
            save_request_file(msg, filename)

            # UNWRAP AND EXECUTE COMMAND
            data = unwrap(filename, version)
            if 'errmfs' in data:
                ret = return_message(command, data)

                if data["errmfs"]["code"] == errmfs.INVALID_SIGNATURE:
                    Error.objects.create(
                        o_computer,
                        o_computer.version,
                        "%s - %s - %s" % (
                            get_client_ip(request),
                            command,
                            errmfs.error_info(errmfs.INVALID_SIGNATURE)
                        )
                    )
            else:
                ret = eval(command)(request, name, uuid, o_computer, data)

            os.remove(filename)
        else:  # Computer not exists
            ret = return_message(
                command,
                errmfs.error(errmfs.COMPUTER_NOT_FOUND)
            )

        # WRAP THE RESULT OF COMMAND
        wrap(filename_return, ret)
        with open(filename_return, 'rb') as fp:
            ret = fp.read()
        os.remove(filename_return)

        return HttpResponse(ret, content_type='text/plain')

    # REGISTERS
    # COMMAND NOT USE KEYS PAIR, ONLY USERNAME AND PASSWORD
    elif command in cmd_register:
        save_request_file(msg, filename)

        with open(filename, "rb") as f:
            data = json.load(f)[command]

        try:
            ret = eval(command)(request, name, uuid, o_computer, data)
        except:
            ret = return_message(command, errmfs.error(errmfs.GENERIC))

        os.remove(filename)

        return HttpResponse(json.dumps(ret), content_type='text/plain')

    # PACKAGER
    elif command in cmd_packager:
        save_request_file(msg, filename)

        # UNWRAP AND EXECUTE COMMAND
        data = unwrap(filename, "migasfree-packager")
        if 'errmfs' in data:
            ret = data
        else:
            ret = eval(command)(request, name, uuid, o_computer, data[command])

        os.remove(filename)

        # WRAP THE RESULT OF COMMAND
        wrap(filename_return, ret)
        with open(filename_return, 'rb') as fp:
            ret = fp.read()
        os.remove(filename_return)

        return HttpResponse(ret, content_type='text/plain')

    else:  # Command not exists
        return HttpResponse(
            return_message(
                command,
                errmfs.error(errmfs.COMMAND_NOT_FOUND)
            ),
            content_type='text/plain'
        )
