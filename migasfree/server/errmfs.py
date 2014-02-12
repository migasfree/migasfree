# -*- coding: UTF-8 -*-

import os
import sys
import traceback
import tempfile

from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from migasfree.settings import MIGASFREE_REPO_DIR

NOAUTHENTICATED = 1
CANNOTREGISTER = 2
METHODGETNOTALLOW = 3
COMMANDNOTFOUND = 4
SIGNNOTOK = 5
COMPUTERNOTFOUND = 6
DEVICENOTFOUND = 7
VERSIONNOTFOUND = 8
USERHAVENOTPERMISSION = 9
GENERIC = 100

DSTR = {
    NOAUTHENTICATED: _("User not authenticated"),
    CANNOTREGISTER: _("User can not register computers"),
    METHODGETNOTALLOW: _("Method GET not allowed"),
    COMMANDNOTFOUND: _("Command not found"),
    SIGNNOTOK: _("Signature is not valid"),
    COMPUTERNOTFOUND: _("Computer not found"),
    DEVICENOTFOUND: _("Device not found"),
    VERSIONNOTFOUND: _("Version not found"),
    USERHAVENOTPERMISSION: _("User have not permission"),
    GENERIC: _("Generic error")
}


def message(number):
    return DSTR[number]


def error(number):
    ret = ''
    if number == GENERIC:
        etype = sys.exc_info()[0]
        evalue = sys.exc_info()[1]

        dir_errors = os.path.join(MIGASFREE_REPO_DIR, 'errors')
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

        fp.write(print_exc_plus(etype,evalue))
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
    return {"errmfs": {"code": 0, "info": _("No errors")}}


def print_exc_plus(etype, evalue):
    """
    Print the usual traceback information, followed by a listing of all the
    local variables in each frame.
    """
    ret = ""
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
        fr = {}
        fr["filename"] = frame.f_code.co_filename
        fr["name"] = frame.f_code.co_name
        fr["line"] = frame.f_lineno

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
