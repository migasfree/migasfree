# -*- coding: utf-8 -*-

import os
import sys
import json
import time

from datetime import timedelta
from datetime import datetime
from datetime import date

from django.utils.translation import ugettext as _
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.db.models import Max
from django.db.models import Count
from django.db.models import Q

from django import forms

from migasfree.settings import MIGASFREE_TMP_DIR
from migasfree.settings import MIGASFREE_REPO_DIR
from migasfree.settings import MIGASFREE_SECONDS_MESSAGE_ALERT

from migasfree.server.open_flash_chart import Chart

from migasfree.server.security import *
from migasfree.server.models import *

from migasfree.server.logic import *
from migasfree.server.forms import ParametersForm
from migasfree.server.api import *
from migasfree.server.load_devices import load_devices

__all__ = (
    # from api
    'api', 'createrepositories', 'createrepositoriesofpackage',
    'directupload', 'message', 'update', 'upload_package', 'upload_set',

    # from chart
    'chart', 'chart_selection', 'daily_updated', 'delay_schedule',
    'hourly_updated', 'monthly_updated', 'version_computer',

    # from device
    'device',

    # from hardware
    'hardware', 'hardware_resume',

    # from query
    'query',

    # from main
    'change_version', 'documentation', 'info', 'login', 'main',
    'query_selection', 'query_message', 'query_message_server',
    'softwarebase', 'system',
)


def user_version(user):
    try:
        userprofile = UserProfile.objects.get(id=user.id)
        return Version.objects.get(id=userprofile.version_id)
    except:
        return None


def option_description(field, value):
    try:
        return field.split(
            '<option value="' + value + '">'
        )[1].split("</option>")[0]
    except:
        return value

# ---- main.py ----


@login_required
def info(request, package):  # package info
    ver = request.GET.get('version')
    if not ver:
        version = user_version(request.user)
    else:
        version = Version.objects.get(name=ver)

    ruta = os.path.join(MIGASFREE_REPO_DIR, version.name, package)

    if os.path.isfile(ruta):
        # GET INFORMATION OF PACKAGE
        cad = "echo \"VERSION: " + version.name + "\"\n"
        cad += "echo \"PACKAGE: " + package[:-1] + "\"\n"
        cad += "echo \n"
        cad += "echo \n"
        cad += "PACKAGE=" + ruta[:-1] + "\n"
        cad += version.pms.info
        ret = run_in_server(cad)["out"]

        return render(
            request,
            'info_package.html',
            {
                "title": _("Information of Package"),
                "contentpage": ret,
            }
        )

    if os.path.isdir(ruta):
        elements = os.listdir(ruta)
        elements.sort()

        # NAVIGATION FOR FOLDERS
        vl_fields = []
        filters = []
        filters.append(package)
        if package > "/":
            vl_fields.append(["folder.png", ".."])

        for e in elements:
            try:
                # TODO: asegurarse de que esto sirve para identificar
                # si es un archivo o un directorio
                if (os.stat(ruta + e).st_mode < 32000):
                    vl_fields.append(["folder.png", e + "/"])
                else:
                    vl_fields.append(["package.png", e + "/"])
            except:
                pass

        return render(
            request,
            'info_folder.html',
            {
                "title": "Information of Package.",
                "description": "VERSION: %s" % version.name,
                "filters": filters,
                "query": vl_fields,
            }
        )

    return HttpResponse(
        'No package info exists.',
        mimetype="text/plain"
    )  # FIXME

@login_required
def query_message(request):
    vl_fields = []

    q = Message.objects.all().order_by("-date")
    t = datetime.now() - timedelta(0, MIGASFREE_SECONDS_MESSAGE_ALERT)

    for e in q:
        if e.date < t:
            icon = 'computer_alert.png'
        else:
            icon = 'computer.png'

        try:
            last = e.computer.last_login()
            user = '%s-%s' % (last.user.name, last.user.fullname)
        except:
            user = "None"

        vl_fields.append(
            [
                icon,
                "-",
                e.computer.id,
                e.computer.name,
                last.id,
                user,
                e.computer.version.name,
                e.computer.ip,
                e.date,
                e.text
            ]
        )

    return render(
        request,
        'message.html',
        {
            "title": _("Computer Messages"),
            "query": vl_fields,
        }
    )


@login_required
def query_message_server(request, param):
    vl_fields = []

    q = MessageServer.objects.all().order_by("-date")

    for e in q:
        icon = 'spinner.gif'

        vl_fields.append(
            [
                icon,
                "-",
                e.date,
                e.text
            ]
        )

    return render(
        request,
        'messageserver.html',
        {
            "title": _("Messages Server"),
            "query": vl_fields,
        }
    )


def login(request):
    if request.method == 'GET':
        return render(
            request,
            'admin/login.html',
        )

    username = request.POST['username']
    password = request.POST['password']

    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        # Correct password, and the user is marked "active"
        auth.login(request, user)
        # Redirect to a success page.
        return HttpResponseRedirect(reverse('bootstrap'))

    # Show the login page
    return HttpResponseRedirect(reverse('login'))


@login_required
def main(request):
    """
    dashboard of migasfree
    """

    status = []

    for obj in Checking.objects.filter(active=True):
        msg = ""
        try:
            exec(obj.code.replace("/r", ""))
            result = vars().get('result', 0)
            if result != 0:
                msg = _(vars().get('msg', obj.name))
                url = vars().get('url', reverse('bootstrap'))
                icon = vars().get('icon', 'information.png')

                status.append(
                    {
                        'icon': icon,
                        'url': url,
                        'result': '%s %s' % (str(result), msg)
                    }
                )
        except:
            return HttpResponse(
                "Error in field 'code' of Checking: %s\n%s" % (
                    msg, str(sys.exc_info())
                ),
                mimetype="text/plain"
            )

    if len(status) == 0:
        status.append(
            {
                'icon': "checking.png",
                'url': "#",
                'result': _("All O.K.")
            }
        )

    return render(
        request,
        'main.html',
        {
            "title": _("Dashboard"),
            "status": status,
        }
    )


@login_required
def system(request):
    """
    System Menu of migasfree
    """

    return render(
        request,
        'system.html',
        {
            "title": _("System Menu"),
        }
    )


@login_required
def query_selection(request):
    """
    Queries Menu of migasfree
    """

    qry = Query.objects.all().order_by("-id")
    vl_fields = []
    for e in qry:
        vl_fields.append([e.id, e.name])

    return render(
        request,
        'query_selection.html',
        {
            "title": _("Queries Menu"),
            "query": vl_fields,
        }
    )


@login_required()
def change_version(request):
    def form_params_version():
        class MyForm(ParametersForm):
            version = forms.ModelChoiceField(Version.objects.all())

        return MyForm

    if request.method == 'POST':
        parameters = {}
        for p in request.POST:
            parameters[p] = request.POST.get(p)

        o_userprofile = UserProfile.objects.get(id=request.user.id)
        o_userprofile.version = Version.objects.get(id=parameters["version"])
        o_userprofile.save()

        return HttpResponseRedirect(reverse('bootstrap'))
    else:

        try:
            oversion = user_version(request.user).id
        except:
            oversion = None

        dic_initial = {
            'user_version': oversion,
            'version': oversion
        }

        g_form_param = form_params_version()(initial=dic_initial)
        request.session['LastUrl'] = request.META.get(
            'HTTP_REFERER', reverse('bootstrap')
        )

        return render(
            request,
            'parameters.html',
            {
                'form': g_form_param,
                'title': _("Change version for %s") % request.user.username,
            }
        )


def softwarebase(request, param):
    version = request.GET.get('VERSION', '')
    try:
        ret = Version.objects.get(name=version).base
    except:
        ret = ""

    return HttpResponse(ret, mimetype="text/plain")


@login_required
def documentation(request):
    """
    Manuals Page
    """

    return render(
        request,
        'documentation.html',
        {
            "title": _("Documentation"),
        }
    )

# ---- api.py ----


def message(request, param):
    """
    Get Messages from Client Computers
    """

    m = time.strftime("%Y-%m-%d %H:%M:%S")
    pc = request.GET.get('PC')
    msg = request.GET.get('TEXT')

    try:
        ocomputer = Computer.objects.get(name=pc)
    except:
        return HttpResponse("Computer not exits", mimetype='text/plain')

    try:
        omessage = Message.objects.get(computer=ocomputer)
        if msg == "":
            omessage.delete()
            Update(
                computer=ocomputer, date=m,
                version=Version.objects.get(name=ocomputer.version)
            ).save()
            return HttpResponse("OK", mimetype='text/plain')
    except:
        omessage = Message(computer=ocomputer)

    omessage.text = msg
    omessage.date = m
    omessage.save()

    return HttpResponse("OK", mimetype='text/plain')


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


def update(request, param):
    """
    DEPRECATED!!!
    Returns script to execute in client machine
    """
    def creaxml(properties, faults):
        ret = '<?xml version="1.0" encoding="UTF-8" standalone= "yes"?>' + "\n"
        ret += "<MIGASFREE>"

        ret += "<COMPUTER>"
        ret += "<HOSTNAME>$HOSTNAME</HOSTNAME>"
        ret += "<IP>`getip | awk 'BEGIN {FS=\"/\"}; {print $1}'`</IP>"
        ret += "<VERSION>$MIGASFREE_VERSION</VERSION>"
        ret += "<USER>$_USER_GRAPHIC</USER>"
        ret += "<USER_FULLNAME>$_USER_FULLNAME</USER_FULLNAME>"
        ret += "</COMPUTER>"

        ret += "<ATTRIBUTES>"
        for e in properties:
            ret += "<" + e.prefix + ">"
            ret += "`" + e.namefunction() + "`"
            ret += "</" + e.prefix + ">"
        ret += "</ATTRIBUTES>"

        ret += "<FAULTS>"
        for e in faults:
            ret += "<" + e.name + ">"
            ret += "`" + e.namefunction() + "`"
            ret += "</" + e.name + ">"
        ret += "</FAULTS>"

        ret += "</MIGASFREE>"

        return ret

    ret = "#!/bin/bash\n\n"
    ret += ". /usr/share/migasfree/init\n\n"

    ret += "_USER_FULLNAME=`cat /etc/passwd|grep $_USER_GRAPHIC|cut -d: -f5|cut -d, -f 1`\n\n"

    ret += "# Entities Functions\n\n"
    properties = Property.objects.filter(active=True)
    for e in properties:
        ret += "function " + e.namefunction() + " {\n"
        ret += e.code.replace("\r", "\n") + "\n"
        ret += "}\n"
        ret += "\n"

    ret += "# Faults Functions\n\n"
    faults = FaultDef.objects.filter(active=True)
    for e in faults:
        ret += "function " + e.namefunction() + " {\n"
        ret += e.code.replace("\r", "\n") + "\n"
        ret += "}\n"
        ret += "\n"

    ret += "# Create the file update.xml\n"
    ret += "tooltip_status \"" + _("Creating Attributes and Faults") + "\"\n"
    ret += "_FILE_XML=\"$_DIR_TMP/update.xml\"\n"
    ret += "cat > $_FILE_XML << EOF\n"
    ret += creaxml(properties, faults) + "\n"
    ret += "EOF\n\n"
    ret += "echo 'Done'\n"

    ret += "# Upload an run update.xml\n"
    ret += "tooltip_status \"" + _("Uploading Attributes and Faults") + "\"\n"
    ret += "directupload_and_run_response $_FILE_XML \n\n"

    return HttpResponse(ret, mimetype='text/plain')


# ejemplo para subir archivos:
# curl -b PC=$HOSTNAME -F file=@$FILE_YUM_LOG http://127.0.0.1:8000/directupload/ > $FILE_RESP
def directupload(request, param):
    """
    Saves the file directly from the request object.
    Disclaimer:  This is code is just an example, and should
    not be used on a real website.  It does not validate
    file uploaded:  it could be used to execute an
    arbitrary script on the server.
    """
    def handle_uploaded_file(f, pc):
        t = time.strftime("%Y-%m-%d")
        m = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            os.makedirs(MIGASFREE_TMP_DIR, 0700)
        except:
            pass
        filename = os.path.join(MIGASFREE_TMP_DIR, '%s.%s' % (pc, f.name))

        def grabar():
            destination = open(filename, 'wb+')
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
            try:
                os.remove(f.temporary_file_path)
            except:
                pass

        ret = f.name + ": no permited upload this file in migasfree.server.views.directupload."

        #SI RECIBIMOS UN FICHERO update.xml
        if f.name == "update.xml":
            grabar()
            destination = open(filename, 'rb')
            ret = process_attributes(request, filename)
            os.remove(filename)
            destination.close()

        #SI RECIBIMOS UN FICHERO history_sw.log
        if f.name == "history_sw.log":
            grabar()
            destination = open(filename, 'rb')

            try:
                computer = Computer.objects.get(name=pc)
            except: #si no esta el Equipo lo añadimos
                computer = Computer(name=pc)
                computer.dateinput = t

            computer.history_sw = str(computer.history_sw) \
                + unicode(destination.read(), "utf-8")
            computer.save()
            os.remove(filename)
            destination.close()
            ret = "OK"

        # SI RECIBIMOS UN FICHERO software.log
        if f.name == "software.log":
            grabar()
            destination = open(filename, 'rb')

            try:
                computer = Computer.objects.get(name=pc)
            except:  # si no esta el Equipo lo añadimos
                computer = Computer(name=pc)
                computer.dateinput = t

            computer.software = unicode(destination.read(), "utf-8")
            computer.save()
            os.remove(filename)
            destination.close()
            ret = "OK"

        # SI RECIBIMOS UN FICHERO base.log
        if f.name == "base.log":
            grabar()
            destination = open(filename, 'rb')

            try:
                oversion = Version.objects.get(
                    name=Computer.objects.get(name=pc).version
                )
            except:  # si no esta el Equipo lo añadimos
                pass
            oversion.base = unicode(destination.read(), "utf-8")
            oversion.save()
            os.remove(filename)
            destination.close()
            ret = "OK"

        # SI RECIBIMOS UN FICHERO DIST.ERR
        if f.name == "migasfree.err":
            grabar()
            destination = open(filename, 'rb')
            try:
                computer = Computer.objects.get(name=pc)
            except:  # si no esta el Equipo lo añadimos
                computer = Computer(name=pc)
                computer.dateinput = t
                computer.save()

            o_error = Error()
            o_error.computer = computer
            o_error.date = m
            o_error.error = unicode(destination.read(), "utf-8")
            o_error.save()
            os.remove(filename)
            destination.close()
            ret = "OK"

        # SI RECIBIMOS UN FICHERO install_device_param (Codigo de instalación de device)
        if f.name == "install_device_param":
            grabar()
            destination = open(filename, 'rb')
            o_device = Device.objects.get(
                name=request.COOKIES.get('NUMBER'),
                connection=DeviceConnection.objects.get(
                    name=request.COOKIES.get('PORT'),
                    devicetype__name=request.COOKIES.get('TYPE')
                )
            )
            o_device.values = unicode(destination.read(), "utf-8")
            o_device.save()

            ret = "OK"
            os.remove(filename)
            destination.close()

#        #SI RECIBIMOS UN FICHERO hardware.xml (Inventario Hardware)
#        if f.name == "hardware.xml":
#            grabar()

#            import codecs
#            destination = codecs.open(filename, "r", "utf-8" )
##            destination = open(filename,'rb')
##            oResumen=pickle.load(destination)
#            try:
#                computer=Computer.objects.get(name=pc)
#            except: #si no esta el Equipo lo añadimos
#                computer=Computer(name=pc)
#                computer.dateinput=t

#            computer.hardware=destination.read()
#            computer.save()
#            ret="OK"
#            os.remove(filename)
#            destination.close()

        # SI RECIBIMOS UN FICHERO hardware.json (Inventario Hardware)
        if f.name == "hardware.json":
            grabar()

            try:
                computer = Computer.objects.get(name=pc)
            except:  # si no esta el Equipo lo añadimos
                computer = Computer(name=pc)
                computer.dateinput = t
            computer.save()

            #process_hw(computer, filename)

            ret = "OK"
            os.remove(filename)

        # SI RECIBIMOS UN FICHERO net-devices.json
        if f.name == "net-devices.json":
            grabar()
            ret = load_devices(filename)
            os.remove(filename)

        return ret

    if request.method == 'POST':
        # Other data on the request.FILES dictionary:
        #   filesize = len(file['content'])
        #   filetype = file['content-type']
        ret = handle_uploaded_file(
            request.FILES['file'],
            request.COOKIES.get('PC')
        )
        return HttpResponse(ret, mimetype='text/plain')

    return HttpResponse("ERROR", mimetype='text/plain')


@login_required
def createrepositories(request, param):
    """
    Create the files of Repositories in the server
    """
    version = user_version(request.user)
    html = create_repositories(version.id)
    return render(
        request,
        "info.html",
        {
            "title": "Create Repository Files.",
            "contentpage": html,
        }
    )


def createrepositoriesofpackage(request, param):
    if request.method != 'GET':
        return HttpResponse("ERROR", mimetype='text/plain')

    username = request.GET.get('username')
    password = request.GET.get('password')
    user = auth.authenticate(username=username, password=password)

    if user is None:
        return HttpResponse(
            "ERROR. User no authenticaded. %s" % request.GET,
            mimetype='text/plain'
        )

    if not user.has_perm("server.can_save_package"):
        return HttpResponse(
            "ERROR. User no have permission for save package. The user must be in the group 'Packager'",
            mimetype='text/plain'
        )

    create_repositories_package(
        request.GET.get('PACKAGE'),
        request.GET.get('VER')
    )

    return HttpResponse('OK', mimetype='text/plain')


def upload_package(request, param):
    def handle_uploaded_file(f, store, version, nopkg):
        def grabar():
            filename = os.path.join(
                MIGASFREE_REPO_DIR,
                version,
                'STORES',
                store,
                f.name
            )
            destination = open(filename, 'wb+')
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
            try:
                os.remove(f.temporary_file_path)
            except:
                pass

        ret = ""

        try:
            oversion = Version.objects.get(name=version)
        except:
            return "No found the version: %s" % version

        # we add the store
        try:
            o_store = Store.objects.get(name=store, version=oversion)
        except:  # if not exists the Store, we add it
            o_store = Store()
            o_store.name = store
            o_store.version = oversion
            o_store.save()

        grabar()

        # we add the package
        if nopkg != "1":
            try:
                o_package = Package.objects.get(name=f.name, version=oversion)
            except:
                o_package = Package(name=f.name, version=oversion)
            o_package.store = o_store
            o_package.save()

        ret = "OK"
        return ret

    if request.method == 'POST':
        # Other data on the request.FILES dictionary:
        #   filesize = len(file['content'])
        #   filetype = file['content-type']

        username = request.COOKIES.get('username')
        password = request.COOKIES.get('password')

        user = auth.authenticate(username=username, password=password)
        if user is None:
            return HttpResponse(
                "ERROR. User no authenticaded.",
                mimetype='text/plain'
            )

        if not user.has_perm("server.can_save_package"):
            return HttpResponse(
                "ERROR. User no have permission for save package. The user must be in the group 'Packager'",
                mimetype='text/plain'
            )

        ret = handle_uploaded_file(
            request.FILES['file'],
            request.COOKIES.get('STORE'),
            request.COOKIES.get('VER'),
            request.COOKIES.get('NOPKG')
        )

        return HttpResponse(ret, mimetype='text/plain')

    return HttpResponse("ERROR", mimetype='text/plain')


def upload_set(request, param):
    def handle_uploaded_file(f, store, version, packageset):

        def grabar():
            filename = os.path.join(
                MIGASFREE_REPO_DIR,
                version,
                'STORES',
                store,
                packageset,
                f.name
            )
            destination = open(filename, 'wb+')
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
            try:
                os.remove(f.temporary_file_path)
            except:
                pass

        ret = ""

        try:
            oversion = Version.objects.get(name=version)
        except:
            return "No found the version: %s" % version

        # we add the store
        try:
            o_store = Store.objects.get(name=store, version=oversion)
        except:  # if not exists the Store, we add it
            o_store = Store()
            o_store.name = store
            o_store.version = oversion
            o_store.save()

        # we add the Package/Set
        try:
            o_package = Package.objects.get(name=packageset, version=oversion)
        except:
            o_package = Package(name=packageset, version=oversion)
        o_package.store = o_store
        o_package.save()
        o_package.create_dir()

        grabar()

        ret = "OK"
        return ret

    if request.method == 'POST':
        # Other data on the request.FILES dictionary:
        #   filesize = len(file['content'])
        #   filetype = file['content-type']

        username = request.COOKIES.get('username')
        password = request.COOKIES.get('password')

        user = auth.authenticate(username=username, password=password)
        if user is None:
            return HttpResponse(
                "ERROR. User no authenticaded.",
                mimetype='text/plain'
            )

        if not user.has_perm("server.can_save_package"):
            return HttpResponse(
                "ERROR. User no have permission for save package. The user must be in the group 'Packager'",
                mimetype='text/plain'
            )

        ret = handle_uploaded_file(
            request.FILES['file'],
            request.COOKIES.get('STORE'),
            request.COOKIES.get('VER'),
            request.COOKIES.get('SET')
        )

        return HttpResponse(ret, mimetype='text/plain')

    return HttpResponse("ERROR", mimetype='text/plain')

# ---- chart.py ----


@login_required
def chart_selection(request):
    """
    Charts Menu of migasfree
    """

    return render(
        request,
        'chart_selection.html',
        {
            "title": _("Charts Menu"),
        }
    )


@login_required
def chart(request, chart_type):
    return render(
        request,
        'chart.html',
        {'ofc': reverse('chart_%s' % chart_type)}
    )


def hourly_updated(request):
    o_chart = Chart()
    timeformat = "%H h. %b %d "
    o_chart.title.text = _("Updated Computers / Hour")
    o_chart.title.style = "{font-size: 18px; color: #417690; text-align: center;}" # FIXME remove

    element1 = Chart()
    element1.values = []
    labels = []

    y = 24 * 4  # 4 days
    delta = timedelta(hours=1)
    n = datetime.now() - ((y - 25) * delta)
    n = datetime(n.year, n.month, n.day, 0)

    for i in range(y):
        value = Update.objects.filter(
            date__gte=n,
            date__lt=n + delta
        ).values('computer').distinct().count()

        element1.values.append(value)
        element1.tip = "#x_label#    #val# " + _("Computers")

        labels.append(n.strftime(timeformat))
        n += delta

    element1.type = "bar"
    # element1.dot_style.type = "dot"
    element1.width = 2
    element1.colour = "#417690"
    element1.text = ""  # Label
    element1.font_size = 10

    o_chart.x_axis.labels.stroke = 3
    o_chart.x_axis.labels.steps = 24
    o_chart.x_axis.labels.rotate = 270

    o_chart.x_axis.labels.labels = labels

    # y_axis
    o_chart.y_axis.max = max(element1.values)
    o_chart.y_axis.steps = 10 ** (len(str(o_chart.y_axis.max * 4)) - 2)
    o_chart.y_axis.max += o_chart.y_axis.steps / 2

    o_chart.elements = [element1, ]
    o_chart.y_legend.text = _("Computers")
    o_chart.y_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove
    o_chart.x_legend.text = _("Hour")
    o_chart.x_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove

    return HttpResponse(o_chart.create(), mimetype="text/plain")


def daily_updated(request):
    o_chart = Chart()
    timeformat = "%b %d"
    o_chart.title.text = _("Updated Computers / Day")
    o_chart.title.style = "{font-size: 18px; color: #417690; text-align: center;}" # FIXME remove

    element1 = Chart()
    element1.values = []
    labels = []

    days = 35
    delta = timedelta(days=1)
    n = date.today() - ((days - 1) * delta)
    for i in range(days):
        value = Update.objects.filter(
            date__gte=n,
            date__lt=n + delta
        ).values('computer').distinct().count()
        element1.values.append(value)
        element1.tip = "#x_label#    #val# " + _("Computers")
        labels.append(n.strftime(timeformat))
        n += delta

    element1.type = "bar"
    element1.dot_style.type = "dot"
    element1.width = 2
    element1.colour = "#417690"
    element1.text = ""  # Label
    element1.font_size = 10

    o_chart.x_axis.labels.rotate = 270
    o_chart.x_axis.labels.labels = labels

    # y_axis
    o_chart.y_axis.max = max(element1.values)
    o_chart.y_axis.steps = 10 ** (len(str(o_chart.y_axis.max * 4)) - 2)
    o_chart.y_axis.max += o_chart.y_axis.steps / 2

    o_chart.elements = [element1, ]

    o_chart.y_legend.text = _("Computers")
    o_chart.y_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove
    o_chart.x_legend.text = _("Day")
    o_chart.x_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove

    return HttpResponse(o_chart.create(), mimetype="text/plain")


def monthly_updated(request):
    o_chart = Chart()
    timeformat = "%b"
    o_chart.title.text = _("Updated Computers / Month")
    o_chart.title.style = "{font-size: 18px; color: #417690; text-align: center;}" # FIXME remove

    element1 = Chart()
    element1.values = []
    labels = []

    year = int(date.today().strftime("%Y"))
    years = [year - 2, year - 1, year]
    months = []
    for i in range(1, 13):
        months.append(date(year, i, 1).strftime(timeformat))

    for y in years:
        for m in range(1, 13):
            value = Update.objects.filter(
                date__month=m,
                date__year=y
            ).values('computer').distinct().count()
            element1.values.append(value)
            element1.tip = "#x_label#    #val# " + _("Computers")
            labels.append(str(months[m - 1]) + " " + str(y))

    element1.type = "bar"
    element1.dot_style.type = "dot"
    element1.width = 2
    element1.colour = "#417690"
    element1.text = ""  # Label
    element1.font_size = 10

    o_chart.x_axis.labels.rotate = 270
    o_chart.x_axis.labels.labels = labels

    # y_axis
    o_chart.y_axis.max = max(element1.values)
    o_chart.y_axis.steps = 10 ** (len(str(o_chart.y_axis.max * 4)) - 2)
    o_chart.y_axis.max += o_chart.y_axis.steps / 2

    o_chart.elements = [element1, ]

    o_chart.y_legend.text = _("Computers")
    o_chart.y_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove
    o_chart.x_legend.text = _("Month")
    o_chart.x_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove

    return HttpResponse(o_chart.create(), mimetype="text/plain")


def delay_schedule(request):
    o_chart = Chart()
    o_chart.title.text = _("Provided Computers / Delay")
    o_chart.title.style = "{font-size: 18px; color: #417690; text-align: center;}" # FIXME remove

    o_chart.elements = []
    o_schedules = Schedule.objects.all()
    # lines = []
    colours = [
        "#fa6900", "#417690", "#C4D318",
        "#FF00FF", "#00FFFF", "#50284A", "#7D7B6A",
    ]
    c = 0
    m = 0
    for sched in o_schedules:
        lst_attributes = []
        line = Chart()
        line.type = "line"
        line.dot_style.type = "dot"
        line.width = 2
        line.colour = colours[c]
        c += 1
        if c == len(colours):
            c = 0

        line.font_size = 10

        d = 1
        value = 0
        line.values = []
        delays = ScheduleDelay.objects.filter(
            schedule__name=sched.name
        ).order_by("delay")
        for delay in delays:
            for i in range(d, delay.delay):
                line.values.append(value)

            for att in delay.attributes.all():
                lst_attributes.append(att.id)

            value = Login.objects.filter(
                Q(attributes__id__in=lst_attributes)
            ).values('computer_id').annotate(lastdate=Max('date')).count()
            print lst_attributes  # DEBUG
            d = delay.delay
        line.values.append(value)
        line.text = sched.name
        line.tip = "#x_label# " + _("days") + " #val# " + _("Computers")

        m = max(m, max(line.values))
        o_chart.elements.append(line)

    o_chart.y_axis.max = m
    o_chart.y_axis.steps = 10 ** (len(str(o_chart.y_axis.max * 4)) - 2)
    o_chart.y_axis.max += o_chart.y_axis.steps / 2

    o_chart.y_legend.text = _("Computers")
    o_chart.y_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove
    o_chart.x_legend.text = _("Delay")
    o_chart.x_legend.style = "{font-size: 12px; color: #778877}"  # FIXME remove

    return HttpResponse(o_chart.create(), mimetype="text/plain")


def version_computer(request):
    o_chart = Chart()
    o_chart.title.text = _("Computers / Version")
    o_chart.title.style = "{font-size: 18px; color: #417690; text-align: center;}" # FIXME remove

    qry = Computer.objects.values("version__name").annotate(count=Count("id"))
    element1 = Chart()
    element1.type = "pie"
    element1.alpha = 0.6
    element1.start_angle = 35
    element1.animate = [{"type": "fade"}, {"type": "bounce", "distance": 10}]
    element1.tip = "#val# " + _("of") + " #total#<br>#percent#"
    element1.colours = ["#1C9E05", "#FF368D", "#417690", "#C4D318", "#50284A"]

    element1.gradient_fill = True
    element1.radius = 100
    element1.values = []
    for e in qry:
        """
        element1.values = [
            2000, 3000, 4000, {
                "value": 6000.511,
                "label": "hello (6000.51)",
                "on-click": "http://example.com"
            }
        ]
        """
        element1.values.append(
            {
                "value": e.get("count"),
                "label": e.get("version__name"),
            }
        )

    o_chart.num_decimals = 0
    o_chart.is_fixed_num_decimals_forced = True
    o_chart.is_decimal_separator_comma = False
    o_chart.is_thousand_separator_disabled = False

    # Add data to chart object
    o_chart.elements = [element1]

    return HttpResponse(o_chart.create(), mimetype="text/plain")

# ---- hardware.py ----


@login_required
def hardware(request, param):
    qry = HwNode.objects.filter(Q(id=param) | Q(parent=param))
    if qry.count > 0:
        computer = qry[0].computer

    return render(
        request,
        'hardware.html',
        {
            "title": computer.name,
            "computer": computer,
            "description": _("Hardware Information"),
            "query": qry,
        }
    )


@login_required
def hardware_resume(request, param):
    qry = HwNode.objects.filter(Q(computer__id=param)).order_by("id")
    if qry.count > 0:
        computer = qry[0].computer

    return render(
        request,
        'hardware_resume.html',
        {
            "title": computer.name,
            "computer": computer,
            "description": _("Hardware Information"),
            "query": qry,
        }
    )

# ---- query.py ----


def query2(request, parameters, form_param):
    o_query = Query.objects.get(id=parameters["id_query"])

    # execute query
    try:
        exec(o_query.code.replace("\r", ""))

        if 'fields' not in vars():
            fields = []
            for key in query.values()[0].iterkeys():
                fields.append(key)

        if 'titles' not in vars():
            titles = fields

        vl_fields = []

        for o in query:
            o = o  # for pylint
            cols = []
            for f in fields:
                cols.append(eval("o.%s" % f))
            vl_fields.append(cols)

        filters = []
        for x in form_param:
            if not (x.name == "id_query" or x.name == "user_version"):
                filters.append('%s: %s' % (
                    str(x.label),
                    parameters[x.name + "_display"]
                ))

        return render(
            request,
            'query.html',
            {
                "title": o_query.name,
                "description": o_query.description,
                "titles": titles,
                "query": vl_fields,
                "filters": filters,
                "row_count": query.count(),
            }
        )
    except:
        return HttpResponse(
            "Error in field 'code' of query:\n" + str(sys.exc_info()),
            mimetype="text/plain"
        )


@login_required
def query(request, query_id):
    if request.method == 'POST':
        parameters = {}
        for p in request.POST:
            parameters[p] = request.POST.get(p)

        o_query = Query.objects.get(id=request.POST.get('id_query', ''))
        dic_initial = {
            'id_query': request.POST.get('id_query', ''),
            'user_version': user_version(request.user).id
        }
        if o_query.parameters == "":
            return query2(request, dic_initial, {})
        else:
            try:
                def form_params():
                    pass

                exec(o_query.parameters.replace("\r", ""))
                g_form_param = form_params()(initial=dic_initial)

                for x in g_form_param:
                    parameters[x.name + "_display"] = option_description(
                        str(x), parameters[x.name]
                    )

                return query2(request, parameters, g_form_param)
            except:
                return HttpResponse(
                    "Error in field 'parameters' of query:\n"
                        + str(sys.exc_info()[1]),
                    mimetype="text/plain"
                )

    # show parameters form
    o_query = Query.objects.get(id=query_id)
    dic_initial = {
        'id_query': query_id,
        'user_version': user_version(request.user).id
    }
    if o_query.parameters == "":
        return query2(request, dic_initial, {})
    else:
        try:
            def form_params():
                pass

            exec(o_query.parameters.replace("\r", ""))
            g_form_param = form_params()(initial=dic_initial)

            return render(
                request,
                'parameters.html',
                {
                    'form': g_form_param,
                    'title': _("Parameters for Query: %s") % o_query.name,
                }
            )
        except:
            return HttpResponse(
                "Error in field 'parameters' of query:\n" + str(sys.exc_info()[1]),
                mimetype="text/plain"
            )

# ---- device.py ----


def device(request, param):
    t = time.strftime("%Y-%m-%d")

    def downfiledevice(pc, devicename, port):
        o_device = Device.objects.get(name=devicename, connection__name=port)
        fileremote = "http://$MIGASFREE_SERVER/repo/" \
            + str(o_device.model.devicefile.name)
        filelocal = "/tmp/migasfree/" + str(o_device.model.devicefile.name)

        ret = ". /usr/share/migasfree/init\n"

        #PARAMS
        ret += "_NAME=" + name_printer(o_device.model.manufacturer.name, o_device.model.name, o_device.name) + "\n"

        # ret += "_NAME=" + o_device.name + "_" + device.model.name + "\n"
        ret += o_device.values + "\n"

        #Download device file
        ret += "mkdir -p /tmp/migasfree/devices\n"
        ret += "if [ \"$MIGASFREE_PROXY\"=\"\" ]; then\n"
        ret += "    wget --no-cache --no-proxy --header=\"Accept: text/plain;q=0.8\" --header=\"Accept-Language: $MIGASFREE_LANGUAGE\" -dnv \"" + fileremote + "\" -O " + filelocal + " 2>/dev/null\n"
        ret += "else\n"
        ret += "    http_proxy=$MIGASFREE_PROXY\n"
        ret += "    wget --no-cache --header=\"Accept: text/plain;q=0.8\" --header=\"Accept-Language: $MIGASFREE_LANGUAGE\" -dnv \"" + fileremote + "\" -O " + filelocal + " 2>/dev/null\n"
        ret += "fi\n\n"

        #Execute code to add printer
        ret += o_device.render_install()
        #Delete device file
        ret += "rm " + filelocal + "\n"

        # Add the device to computer
        try:
            o_computer = Computer.objects.get(name=pc)
        except:  # si no esta el Equipo lo añadimos
            o_computer = Computer(name=pc)
            o_computer.version = Version.objects.get(id=1)
            o_computer.dateinput = t
            o_computer.save()

        o_computer.devices.add(o_device.id)
        o_computer.save()

        return ret

    def selection(number, title, options):
        if (len(options) <= 1) and (title == "TYPE" or title == "PORT"):
            ret = "_" + title + "=\"" + options[0] + "\"\n"
        else:
            ret = "dialog --backtitle \"migasfree - INSTALL DEVICE " \
                + number + "\" --menu \"" + title + "\" 0 0 0"

            i = 0
            for o in options:
                ret += " \"" + str(i) + "\" \"" + o + "\""
                i += 1

            ret += " 2>/tmp/ans\n"
            ret += "#CANCEL\n"
            ret += "if [ $? = 1 ]\n then\n"
            ret += "   rm -f /tmp/ans\n"
            ret += "   clear\n"
            ret += "   exit 0\n"
            ret += "fi\n"
            ret += "_OPCION=\"`cat /tmp/ans`\"\n"
            ret += "clear\n"

            i = 0
            for o in options:
                ret += "if [ $_OPCION = \"" + str(i) + "\" ] \n  then\n"
                ret += "_" + title + "=\"" + o + "\"\n"
                ret += "fi\n"
                i += 1

        return ret

    def list_type():
        l = []
        types = DeviceType.objects.all()
        for o in types:
            l.append(o.name)
        return l

    def list_manufacturer(devicetype):
        l = []
        manufacturers = DeviceManufacturer.objects.filter(
            devicemodel__devicetype__name=devicetype
        ).distinct()
        for o in manufacturers:
            l.append(o.name)

        return l

    def list_model(devicetype, manufacturer):
        l = []
        o_models = DeviceModel.objects.filter(
            devicetype__name=devicetype, manufacturer__name=manufacturer
        )
        for o in o_models:
            l.append(o.name)

        return l

    def list_port(model):
        l = []
        o_connections = DeviceConnection.objects.filter(devicemodel__name=model)
        for o in o_connections:
            l.append(o.name)

        return l

    def whatdevicetype(number):
        ret = "#!/bin/bash\n"
        ret += "#whatmodel\n"
        ret += ". /usr/share/migasfree/init\n"
        ret += "_FILE_MIGAS=/tmp/install_device_type\n"
        ret += "chmod 700 $_FILE_MIGAS\n"
        ret += "_NUMBER=" + number + "\n"
        ret += selection(number, "TYPE", list_type())
        ret += "download_file \"device/?CMD=install&HOST=$HOSTNAME&TYPE=$_TYPE&NUMBER=$_NUMBER\" \"$_FILE_MIGAS\"\n"

        ret += "if [ $? == 0 ]\n  then\n"
        ret += "   chmod 700 $_FILE_MIGAS\n"
        ret += "   $_FILE_MIGAS\n"
        ret += "fi\n"

        return ret

    def whatdevicemanufacturer(number, devicetype):
        ret = "#!/bin/bash\n"
        ret += "#whatmanufacturer\n"
        ret += ". /usr/share/migasfree/init\n"
        ret += "_FILE_MIGAS=/tmp/install_device_manufacturer\n"
        ret += "chmod 700 $_FILE_MIGAS\n"
        ret += "_NUMBER=" + number + "\n"
        ret += "_TYPE=" + devicetype + "\n"
        ret += selection(number, "MANUFACTURER", list_manufacturer(devicetype))
        ret += "download_file \"device/?CMD=install&HOST=$HOSTNAME&MANUFACTURER=$_MANUFACTURER&TYPE=$_TYPE&NUMBER=$_NUMBER\"  \"$_FILE_MIGAS\"\n"

        ret += "if [ $? == 0 ]\n  then\n"
        ret += "   chmod 700 $_FILE_MIGAS\n"
        ret += "   $_FILE_MIGAS\n"
        ret += "fi\n"

        return ret

    def whatmodel(number, devicetype, manufacturer):
        ret = "#!/bin/bash\n"
        ret += "#whatmodel\n"
        ret += ". /usr/share/migasfree/init\n"
        ret += "_FILE_MIGAS=/tmp/install_device_model\n"
        ret += "chmod 700 $_FILE_MIGAS\n"
        ret += "_NUMBER=" + number + "\n"
        ret += "_TYPE=" + devicetype + "\n"
        ret += "_MANUFACTURER=" + manufacturer + "\n"
        ret += selection(number, "MODEL", list_model(devicetype, manufacturer))
        ret += "download_file \"device/?CMD=install&HOST=$HOSTNAME&MODEL=$_MODEL&MANUFACTURER=$_MANUFACTURER&TYPE=$_TYPE&NUMBER=$_NUMBER\" \"$_FILE_MIGAS\"\n"

        ret += "if [ $? == 0 ]\n  then\n"
        ret += "   chmod 700 $_FILE_MIGAS\n"
        ret += "   $_FILE_MIGAS\n"
        ret += "fi\n"

        return ret

    def whatport(number, devicetype, manufacturer, model):
        ret = "#!/bin/bash\n"
        ret += "#whatport\n"
        ret += ". /usr/share/migasfree/init\n"
        ret += "_FILE_MIGAS=/tmp/install_device_port\n"
        ret += "chmod 700 $_FILE_MIGAS\n"
        ret += "_NUMBER=" + number + "\n"
        ret += "_TYPE=" + devicetype + "\n"
        ret += "_MANUFACTURER=" + manufacturer + "\n"
        ret += "_MODEL=" + model + "\n"
        ret += selection(number, "PORT", list_port(model))
        ret += "download_file \"device/?CMD=install&HOST=$HOSTNAME&MODEL=$_MODEL&MANUFACTURER=$_MANUFACTURER&TYPE=$_TYPE&NUMBER=$_NUMBER&PORT=$_PORT\" \"$_FILE_MIGAS\"\n"

        ret += "if [ $? == 0 ]\n then\n"
        ret += "   chmod 700 $_FILE_MIGAS\n"
        ret += "   $_FILE_MIGAS\n"
        ret += "fi\n"

        return ret

    def processmodel(number, devicetype, manufacturer, model, port):
        ret = "#!/bin/bash\n"
        ret += "#processmodel\n"
        ret += ". /usr/share/migasfree/init\n"
        ret += "_FILE_MIGAS=/tmp/install_device_code\n"
        ret += "_FILE_MIGAS_PARAM=/tmp/install_device_param\n"
        ret += "_FILE_RESP=/tmp/resp\n"

        o_devicemodel = DeviceModel.objects.get(name=model)
        o_deviceconnection = DeviceConnection.objects.get(
            name=port, devicetype__name=devicetype
        )

        fields = o_deviceconnection.fields.split()
        ret += "rm -f $_FILE_MIGAS_PARAM\n"

        ret += "_NAME='" + name_printer(manufacturer, model, number) + "'\n"
        ret += "echo ""_NAME='" + name_printer(manufacturer, model, number) + "'"" >>$_FILE_MIGAS_PARAM\n"
        for f in fields:
            ret += "dialog --backtitle \"migasfree - INSTALL DEVICE " + number + "\" --inputbox \"" + f + "\" 0 0 2>/tmp/ans\n"
            ret += "#CANCEL\n"
            ret += "if [ $? = 1 ]\n  then\n"
            ret += "  rm -f /tmp/ans\n"
            ret += "  clear\n"
            ret += "  exit 0\n"
            ret += "fi\n"
            ret += "_" + f + "=\"`cat /tmp/ans`\"\n"
            ret += "echo \"_" + f + "=\'$_" + f + "\'\" >>$_FILE_MIGAS_PARAM\n"

        #We add the device
        o_device = Device()
        o_device.name = number
        o_device.model = o_devicemodel
        o_device.connection = o_deviceconnection
        o_device.save()

        #Actualize the device
        ret += "upload_file \"$_FILE_MIGAS_PARAM\" directupload/ \"PC=$HOSTNAME;TYPE=" + devicetype + ";NUMBER=" + number + ";MODEL=" + model + ";PORT=" + port + "\"\n"

        ret += "cat > $_FILE_MIGAS << EOF \n"
        ret += ". $_FILE_MIGAS_PARAM\n"
        ret += downfiledevice(host, number, port) + "\n"
        ret += "EOF\n"
        ret += "chmod 700 $_FILE_MIGAS\n"
        ret += "$_FILE_MIGAS\n"

        return ret

    host = request.GET.get('HOST', '')
    number = request.GET.get('NUMBER', '')
    devicetype = request.GET.get('TYPE', '')
    manufacturer = request.GET.get('MANUFACTURER', '')
    model = request.GET.get('MODEL', '')
    port = request.GET.get('PORT', '')
    cmd = request.GET.get('CMD', '')

    if cmd == "install":
        #Reinstall all printer configurated in migasfree
        if number == "ALL":
            cursor = Device.objects.filter(computer__name=host)
            ret = ""
            for c in cursor:
                ret += downfiledevice(host, c.name, c.connection.name)

            return HttpResponse(ret, mimetype="text/plain")

        if port == "":
            cursor = Device.objects.filter(name=number)
        else:
            cursor = Device.objects.filter(name=number, connection__name=port)
            if len(cursor) == 1:
                ret = downfiledevice(host, number, port)

                return HttpResponse(ret, mimetype="text/plain")

        if len(cursor) > 0:  # Si se ha configurado alguna vez el dispositivo
            model = cursor[0].model.name
            deviceconnection = DeviceConnection.objects.filter(devicemodel__name=model)
            if len(deviceconnection) == 1:  # SI el modelo tiene 1 conexion
                ret = downfiledevice(host, number, deviceconnection[0].name)
                return HttpResponse(ret, mimetype="text/plain")
            else:  # SI el modelo no tiene 1 conexion
                if port == "":
                    ret = whatport(
                        number,
                        DeviceModel.objects.get(name=model).devicetype.name,
                        DeviceModel.objects.get(name=model).manufacturer.name,
                        model
                    )
                    return HttpResponse(ret, mimetype="text/plain")
                else:
                    #Existe un device con este port ya configurado?
                    cursor = cursor.filter(connection__name=port)
                    if len(cursor) == 1:
                        ret = downfiledevice(host, number, port)
                        return HttpResponse(ret, mimetype="text/plain")
                    else:
                        ret = processmodel(
                            number,
                            DeviceModel.objects.get(name=model).devicetype.name,
                            DeviceModel.objects.get(name=model).manufacturer.name,
                            model,
                            port
                        )
                        return HttpResponse(ret, mimetype="text/plain")

        else: #si no está el Device lo añadimos
            # Pedimos el device type
            if devicetype == "":
                ret = whatdevicetype(number)
                return HttpResponse(ret, mimetype="text/plain")

            # Pedimos el fabricante
            if manufacturer == "":
                ret = whatdevicemanufacturer(number, devicetype)
                return HttpResponse(ret, mimetype="text/plain")

            # Pedimos el modelo
            if model == "":
                ret = whatmodel(number, devicetype, manufacturer)
                return HttpResponse(ret, mimetype="text/plain")

            # Pedimos el puerto
            if port == "":
                ret = whatport(number, devicetype, manufacturer, model)
                return HttpResponse(ret, mimetype="text/plain")

            # Devolvemos el script para la instalacion
            else:
                ret = processmodel(number, devicetype, manufacturer, model, port)

                return HttpResponse(ret, mimetype="text/plain")
