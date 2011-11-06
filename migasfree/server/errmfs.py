# -*- coding: UTF-8 -*-

import os
import sys
import traceback
import tempfile

from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.template import Context

from migasfree.server.functions import trans
from migasfree.settings import MIGASFREE_REPO_DIR
from migasfree.settings import STATIC_URL

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
    NOAUTHENTICATED: trans("User not authenticated"),
    CANNOTREGISTER: trans("User can not register computers"),
    METHODGETNOTALLOW: trans("Method GET not allowed"),
    COMMANDNOTFOUND: trans("Command not found"),
    SIGNNOTOK: trans("Signature is not valid"),
    COMPUTERNOTFOUND: trans("Computer not found"),
    DEVICENOTFOUND: trans("Device not found"),
    VERSIONNOTFOUND: trans("Version not found"),
    USERHAVENOTPERMISSION: trans("User have not permission"),
    GENERIC: trans("Generic error")
}

def message(number):
    return DSTR[number]

def error(number):
    ret = ''
    if number == GENERIC:
        etype = sys.exc_info()[0]
        evalue = sys.exc_info()[1]
        _subdir = "errors"
        _dir_errors = os.path.join(MIGASFREE_REPO_DIR, _subdir)
        if not os.path.exists(_dir_errors):
            os.makedirs(_dir_errors)

        fp = tempfile.NamedTemporaryFile(
            mode='w+b',
            bufsize=-1,
            suffix='.html',
            prefix=str(evalue).replace(" ", "_").replace("\n", "_"),
            dir=_dir_errors,
            delete=False
        )

        fp.write(print_exc_plus(etype,evalue))
        fp.close()
        ret = str(etype) + " " + str(evalue) + "Traceback: " + os.path.join(STATIC_URL, _subdir, os.path.basename(fp.name))

    return {"errmfs": {"code": number, "info": ret}}

def ok():
    return {"errmfs": {"code": 0, "info": trans("No errors")}}

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
    ret=[]
    for frame in stack:
        fr={}
        fr["filename"] = frame.f_code.co_filename
        fr["name"] = frame.f_code.co_name
        fr["line"] = frame.f_lineno
        variables=[]
        for key, value in frame.f_locals.items():
            try:
                variables.append({"key": key, "value": str(value)})
            except:
                pass
        fr["locals"] = variables
        ret.append(fr)

    return render_to_string(
        'error.html',
        Context(
            {
                "description": _("Error generic in server:") + str(etype) + " " + str(evalue),
                "traceback": ret
            }
        )
    )
