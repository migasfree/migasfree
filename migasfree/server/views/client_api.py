# -*- coding: utf-8 -*-

import os
import json
import time

from datetime import datetime

from django.utils.translation import ugettext as _
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse

from migasfree.settings import MIGASFREE_TMP_DIR
from migasfree.settings import MIGASFREE_REPO_DIR

from migasfree.server.security import *
from migasfree.server.models import *

from migasfree.server.logic import *
from migasfree.server.api import *
from migasfree.server.views import load_devices


def api(request, param):
    message = "message"

    # USING USERNAME AND PASSWORD ONLY (WITHOUT KEYS PAIR)
    functs_register = {
        "register_computer": register_computer,
        "get_key_packager": get_key_packager
    }

    # USING "PACKAGER" KEYS PAIR
    functs_packager = {
        "upload_server_package": upload_server_package,
        "upload_server_set": upload_server_set,
        "create_repositories_of_packageset": create_repositories_of_packageset
    }

    # USING "VERSION" KEYS
    functs_version = {
        "upload_computer_message": upload_computer_message,
        "get_properties": get_properties,
        "upload_computer_info": upload_computer_info,
        "upload_computer_faults": upload_computer_faults,
        "upload_computer_hardware": upload_computer_hardware,
        "upload_computer_software_base_diff": upload_computer_software_base_diff,
        "upload_computer_software_base": upload_computer_software_base,
        "upload_computer_software_history": upload_computer_software_history,
        "get_computer_software": get_computer_software,
        "upload_computer_errors": upload_computer_errors,
        "get_device": get_device,
        "get_assist_devices": get_assist_devices,
        "install_device": install_device,
        "remove_device": remove_device
    }

    if request.method == 'POST':
        # Other data on the request.FILES dictionary:
        #   filesize = len(file['content'])
        #   filetype = file['content-type']

        f = request.FILES[message]
        try:
            os.makedirs(MIGASFREE_TMP_DIR, 0700)
        except:
            pass
        filename = os.path.join(MIGASFREE_TMP_DIR, f.name)
        filename_return = "%s.return" % filename

        # check command
        command = f.name.split(".")[-1]

        # CHECK COMPUTER
        computer = f.name[0:-len(command) - 1]

        # COMPUTERS
        if command in functs_version:  # IF COMMAND IS BY VERSION
            if Computer.objects.filter(name=computer):
                version = Computer.objects.get(name=computer).version.name
                save_request_file(request.FILES[message], filename)

                # UNWRAP AND EXECUTE COMMAND
                data = unwrap(filename, version)
                if 'errmfs' in data:
                    ret = return_message(command, data)

                    if data["errmfs"]["code"] == errmfs.SIGNNOTOK:
                        # add an error
                        oerr = Error()
                        oerr.computer = Computer.objects.get(name=computer)
                        oerr.version = Version.objects.get(name=version)
                        oerr.error = "%s - %s " % (
                            command,
                            errmfs.message(errmfs.SIGNNOTOK)
                        )
                        oerr.date = datetime.now()
                        oerr.save()

                else:
                    ret = functs_version[command](request, computer, data)

                os.remove(filename)
            else:  # Computer not exists
                ret = return_message(
                    command,
                    errmfs.error(errmfs.COMPUTERNOTFOUND)
                )

            # WRAP THE RESULT OF COMMAND
            wrap(filename_return, ret)
            fp = open(filename_return, 'rb')
            ret = fp.read()
            fp.close()
            os.remove(filename_return)

            return HttpResponse(ret, mimetype='text/plain')

        # REGISTERS
        # COMMAND NOT USE KEYS PAIR, ONLY USERNAME AND PASSWORD
        elif command in functs_register:
            save_request_file(request.FILES[message], filename)

            with open(filename, "rb") as f:
                data = json.load(f)[command]
            f.close()

            try:
 #               username = data["username"]
 #               password = data["password"]
 #               user = auth.authenticate(username=username, password=password)
 #               if user is None:
                    #TODO registrar el intento fallido
 #                   ret =  return_message(command, errmfs.error(errmfs.NOAUTHENTICATED))
 #               else:
 #                   ret = functs_register[command](request, computer, data)
                ret = functs_register[command](request, computer, data)
            except:
                ret = return_message(command, errmfs.error(errmfs.GENERIC))

            os.remove(filename)

            return HttpResponse(json.dumps(ret), mimetype='text/plain')

        # PACKAGER
        elif command in functs_packager:
            save_request_file(request.FILES[message], filename)

            # UNWRAP AND EXECUTE COMMAND
            data = unwrap(filename, "migasfree-packager")
            if 'errmfs' in data:
                ret = data
            else:
                ret = functs_packager[command](request, computer, data[command])

            os.remove(filename)

            # WRAP THE RESULT OF COMMAND
            wrap(filename_return, ret)
            fp = open(filename_return, 'rb')
            ret = fp.read()
            fp.close()
            os.remove(filename_return)

            return HttpResponse(ret, mimetype='text/plain')

        else:  # Command not exists
            return HttpResponse(
                return_message(
                    command,
                    str(errmfs.error(errmfs.COMMANDNOTFOUND))
                ),
                mimetype='text/plain'
            )

    # Not allow method 'GET'
    return HttpResponse(
        return_message(
            command,
            str(errmfs.error(errmfs.METHODGETNOTALLOW))
        ),
        mimetype='text/plain'
    )
