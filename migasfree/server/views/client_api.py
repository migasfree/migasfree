# -*- coding: utf-8 -*-

import os
import json

from datetime import datetime

from django.http import HttpResponse

from migasfree.settings import MIGASFREE_TMP_DIR

from migasfree.server.models import Error
from migasfree.server.api import *
from migasfree.server.errmfs import *
from migasfree.server.security import *
from migasfree.server.functions import get_client_ip


def api(request):
    # Other data on the request.FILES dictionary:
    #   filesize = len(file['content'])
    #   filetype = file['content-type']

    msg = request.FILES.get('message')
    filename = os.path.join(MIGASFREE_TMP_DIR, msg.name)
    filename_return = "%s.return" % filename

    lst_msg = msg.name.split('.')
    if len(lst_msg) == 2:  # COMPATIBILITY WITHOUT UUID
        name, command = lst_msg
        uuid = name
    else:  # WITH UUID
        name = ".".join(lst_msg[:-2])
        uuid = lst_msg[-2]
        command = lst_msg[-1]

    o_computer = get_computer(name, uuid)

    if request.method != 'POST':
        return HttpResponse(
            return_message(
                command,
                errmfs.error(errmfs.METHODGETNOTALLOW)
            ),
            mimetype='text/plain'
        )

    if not os.path.exists(MIGASFREE_TMP_DIR):
        try:
            os.makedirs(MIGASFREE_TMP_DIR, 0o700)
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
        "get_device",
        "get_assist_devices",
        "install_device",
        "remove_device",
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

                if data["errmfs"]["code"] == errmfs.SIGNNOTOK:
                    # add an error
                    oerr = Error()
                    oerr.computer = o_computer
                    oerr.version = o_computer.version
                    oerr.error = "%s - %s - %s" % (
                        get_client_ip(request),
                        command,
                        errmfs.message(errmfs.SIGNNOTOK)
                    )
                    oerr.date = datetime.now()
                    oerr.save()
            else:
                ret = eval(command)(request, name, uuid, o_computer, data)

            os.remove(filename)
        else:  # Computer not exists
            ret = return_message(
                command,
                errmfs.error(errmfs.COMPUTERNOTFOUND)
            )

        # WRAP THE RESULT OF COMMAND
        wrap(filename_return, ret)
        with open(filename_return, 'rb') as fp:
            ret = fp.read()
        os.remove(filename_return)

        return HttpResponse(ret, mimetype='text/plain')

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

        return HttpResponse(json.dumps(ret), mimetype='text/plain')

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

        return HttpResponse(ret, mimetype='text/plain')

    else:  # Command not exists
        return HttpResponse(
            return_message(
                command,
                errmfs.error(errmfs.COMMANDNOTFOUND)
            ),
            mimetype='text/plain'
        )
