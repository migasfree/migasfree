# -*- coding: UTF-8 -*-

import os
import sys
import traceback
import tempfile

from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import ugettext as _


ALL_OK = 0
UNAUTHENTICATED = 1
CAN_NOT_REGISTER_COMPUTER = 2
GET_METHOD_NOT_ALLOWED = 3
COMMAND_NOT_FOUND = 4
INVALID_SIGNATURE = 5
COMPUTER_NOT_FOUND = 6
DEVICE_NOT_FOUND = 7
VERSION_NOT_FOUND = 8
USER_DOES_NOT_HAVE_PERMISSION = 9
UNSUBSCRIBED_COMPUTER = 10
GENERIC = 100

ERROR_INFO = {
    ALL_OK: _("No errors"),
    UNAUTHENTICATED: _("User unauthenticated"),
    CAN_NOT_REGISTER_COMPUTER: _("User can not register computers"),
    GET_METHOD_NOT_ALLOWED: _("Method GET not allowed"),
    COMMAND_NOT_FOUND: _("Command not found"),
    INVALID_SIGNATURE: _("Signature is not valid"),
    COMPUTER_NOT_FOUND: _("Computer not found"),
    DEVICE_NOT_FOUND: _("Device not found"),
    VERSION_NOT_FOUND: _("Version not found"),
    USER_DOES_NOT_HAVE_PERMISSION: _("User does not have permission"),
    UNSUBSCRIBED_COMPUTER: _("Unsubscribed computer"),
    GENERIC: _("Generic error")
}


def error_info(number):
    """
    string error_info(int number)
    """
    return ERROR_INFO.get(number, '')


def error(number):
    ret = error_info(number)
    if settings.DEBUG and number == GENERIC:
        etype = sys.exc_info()[0]
        evalue = sys.exc_info()[1]

        dir_errors = os.path.join(settings.MIGASFREE_PUBLIC_DIR, 'errors')
        if not os.path.exists(dir_errors):
            os.makedirs(dir_errors)

        fp = tempfile.NamedTemporaryFile(
            mode='w+b',
            bufsize=-1,
            suffix='.html',
            prefix=str(evalue).replace(" ", "_").replace("\n", "_"),
            dir=dir_errors,
            delete=False
        )

        fp.write(print_exc_plus(etype, evalue))
        fp.close()

        ret = '%s %s %s: %s' % (
            str(etype),
            str(evalue),
            _("Traceback"),
            os.path.join(
                dir_errors,
                os.path.basename(fp.name)
            )
        )

    return {"errmfs": {"code": number, "info": ret}}


def ok():
    return error(ALL_OK)


def print_exc_plus(etype, evalue):
    """
    Print the usual traceback information, followed by a listing of all the
    local variables in each frame.
    """
    tb = sys.exc_info()[2]
    while 1:
        if not tb.tb_next:
            break
        tb = tb.tb_next

    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back

    stack.reverse()
    traceback.print_exc()

    ret = []
    for frame in stack:
        fr = {
            'filename': frame.f_code.co_filename,
            'name': frame.f_code.co_name,
            'line': frame.f_lineno
        }

        variables = []
        for key, value in frame.f_locals.items():
            try:
                variables.append({"key": key, "value": str(value)})
            except:
                pass

        fr["locals"] = variables
        ret.append(fr)

    return render_to_string(
        'error.html',
        {
            "description": '%s: %s %s' % (
                _("Generic error in server"),
                str(etype),
                str(evalue)
            ),
            "traceback": ret
        }
    )
