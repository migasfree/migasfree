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
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.db.models import Max
from django.db.models import Count
from django.db.models import Q

from django.template import Context
from django import forms

from migasfree.settings import MIGASFREE_TMP_DIR
from migasfree.settings import MIGASFREE_REPO_DIR
from migasfree.settings import MIGASFREE_SECONDS_MESSAGE_ALERT

import migasfree.server.errmfs
from migasfree.server.open_flash_chart import Chart

from migasfree.server.security import *
from migasfree.server.models import *

from migasfree.server.logic import *
from migasfree.server.forms import ParametersForm
from migasfree.server.api import *

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
    'query_selection', 'query_message', 'softwarebase', 'system',
)

def user_version(user):
    try:
        userprofile = UserProfile.objects.get(id=user.id)
        return Version.objects.get(id=userprofile.version_id)
    except:
        return None

def option_description(field, value):
    try:
        return field.split('<option value="' + value + '">')[1].split("</option>")[0]
    except:
        return value

# ---- main.py ----

@login_required
def info(request, param):
    version = user_version(request.user)
    ruta = os.path.join(MIGASFREE_REPO_DIR, version.name, param)

    try:
        elements = os.listdir(ruta)
    except:
        # GET INFORMATION OF PACKAGE
        cad = "echo \"VERSION: " + version.name + "\"\n"
        cad += "echo \"PACKAGE: " + param[:-1] + "\"\n"
        cad += "echo \n"
        cad += "echo \n"
        cad += "PACKAGE=" + ruta[:-1] + "\n"
        cad += version.pms.info
        ret = run_in_server(cad)["out"]

        return render_to_response(
            'info_package.html',
            {
                "title": _("Information of Package"),
                "contentpage": ret,
                "user": request.user,
                "root_path": "/migasfree/admin/",
                "LANGUAGE_CODE": request.LANGUAGE_CODE
            }
        )

    # NAVIGATION FOR FOLDERS
    vl_fields = []
    filters = []
    filters.append(param)
    if param > "/":
        vl_fields.append(["folder.png", ".."])

    for e in elements:
        try:
            if (os.stat(ruta + e).st_mode < 32000): #TODO: asegurarse de que esto sirve para identificar si es un archivo o un directorio
                vl_fields.append(["folder.png", e + "/"])
            else:
                vl_fields.append(["package.png", e + "/"])
        except:
            pass

    return render_to_response(
        'info_folder.html',
        {
            "title": "Information of Package.",
            "description": "VERSION: %s" % version.name,
            "filters": filters,
            "query": vl_fields,
            "user": request.user,
            "root_path": "/migasfree/admin/"
        }
    )

@login_required
def query_message(request, param):
    vl_fields = []

    q = Message.objects.all().order_by("-date")
    t = datetime.now() - timedelta(0, MIGASFREE_SECONDS_MESSAGE_ALERT)

    q = Message.objects.all()

    for e in q:
        if e.date < t:
            icon = 'computer_alert.png'
        else:
            icon = 'computer.png'

        last = e.computer.last_login()
        vl_fields.append(
            [
                icon,
                "-",
                e.computer.id,
                e.computer.name,
                last.id,
                last.user.name + "-" + last.user.fullname,
                e.computer.version.name,
                e.computer.ip,
                e.date,
                e.text
            ]
        )

    return render_to_response(
        'message.html',
        {
            "title": _("Computer Messages"),
            "query": vl_fields,
            "user": request.user,
            "root_path": "/migasfree/admin/"
        }
    )

def login(request, param):
    if request.method == 'GET':
        return render_to_response(
            'admin/login.html',
            {
                "user": request.user,
                "root_path": "/migasfree/admin/"
            }
        )

    username = request.POST['username']
    password = request.POST['password']

    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        # Correct password, and the user is marked "active"
        auth.login(request, user)
        # Redirect to a success page.
        return HttpResponseRedirect("/migasfree/main/")

    # Show the login page
    return HttpResponseRedirect("/migasfree/login/")

def main(request, param):
    """
    Main Menu of migasfree
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/migasfree/login')

    status = []
    filters = []
    filters.append(param)

    for obj in Checking.objects.filter(active=True):
        msg = ""
        try:
            exec(obj.code.replace("/r", ""))
            if vars().has_key("result") == True:
                result = vars()["result"]
                if result != 0:
                    if vars().has_key("msg") == False:
                        msg = _(obj.name)
                    else:
                        msg = _(vars()["msg"])

                    if vars().has_key("url") == False:
                        url = "/migasfree/main"
                    else:
                        url = vars()["url"]

                    if vars().has_key("icon") == False:
                        icon = "information.png"
                    else:
                        icon = vars()["icon"]

                    status.append({
                        'icon': icon,
                        'url': url,
                        'result': str(result) + " " + msg
                    })
        except:
            return HttpResponse(
                "Error in field 'code' of Checking: " + msg + "\n" + str(sys.exc_info()),
                mimetype="text/plain"
            )

    if len(status) == 0:
        status.append({
            'icon': "checking.png",
            'url': "#",
            'result': _("All O.K.")
        })

    return render_to_response(
        'main.html',
        {
            "title": _("Main Menu"),
            "description": "",
            "filters": filters,
            "status": status,
            "user": request.user,
            "root_path": "/migasfree/admin/",
            "LANGUAGE_CODE": request.LANGUAGE_CODE
        }
    )

def system(request, param):
    """
    System Menu of migasfree
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/migasfree/login')

    status = []
    filters = []
    filters.append(param)

    return render_to_response(
        'system.html',
        {
            "title": _("System Menu"),
            "description": "",
            "filters": filters,
            "status": status,
            "user": request.user,
            "root_path": "/migasfree/admin/",
            "LANGUAGE_CODE": request.LANGUAGE_CODE
        }
    )

def query_selection(request, param):
    """
    Queries Menu of migasfree
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/migasfree/login')

    qry = Query.objects.all().order_by("-id")
    vl_fields = []
    for e in qry:
        vl_fields.append([e.id, e.name])

    return render_to_response(
        'query_selection.html',
        {
            "title": _("Queries Menu"),
            "query": vl_fields,
            "user": request.user,
            "root_path": "/migasfree/admin/",
            "LANGUAGE_CODE": request.LANGUAGE_CODE
        }
    )

@login_required()
def change_version(request, param):
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

        return HttpResponseRedirect('/migasfree/main')
    else:
        dic_initial = {
            'user_version': user_version(request.user).id,
            "root_path": "/migasfree/admin",
            'version': user_version(request.user).id
        }
        g_form_param = form_params_version()(initial=dic_initial)
        try:
            request.session["LastUrl"] = request.META["HTTP_REFERER"]
        except:
            request.session["LastUrl"] = "/migasfree/main"

        return render_to_response(
            'parameters.html',
            {
                'form': g_form_param,
                'title': _("Change version for %s") % request.user.username,
                "user": request.user,
                "root_path": "/migasfree/admin/"
            }
        )

def softwarebase(request, param):
    version = request.GET.get('VERSION', '')
    try:
        ret = Version.objects.get(name=version).base
    except:
        ret = ""

    return HttpResponse(ret, mimetype="text/plain")

def documentation(request, param):
    """
    Manuals Page
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/migasfree/login')

    filters = []
    filters.append(param)

    return render_to_response(
        'documentation.html',
        {
            "title": _("Documentation"),
            "description": "",
            "filters": filters,
            "user": request.user,
            "root_path": "/migasfree/admin/",
            "LANGUAGE_CODE": request.LANGUAGE_CODE
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
        computer = Computer.objects.get(name=pc)
    except:
        return HttpResponse("Computer not exits", mimetype='text/plain')

    try:
        omessage = Message.objects.get(computer=computer)
        if msg == "":
            omessage.delete()
            Update(computer=computer, date=m).save()
            return HttpResponse("OK", mimetype='text/plain')
    except:
        omessage = Message(computer=computer)

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
        computer = f.name[0:-len(command)-1]

        # COMPUTERS
        if functs_version.has_key(command): # IF COMMAND IS BY VERSION
            if Computer.objects.filter(name=computer):
                version = Computer.objects.get(name=computer).version.name
                save_request_file(request.FILES[message], filename)

                # UNWRAP AND EXECUTE COMMAND
                data = unwrap(filename, version)
                if data.has_key("errmfs"):
                    ret = return_message(command, data)
                else:
                    ret = functs_version[command](request, computer, data)

                os.remove(filename)
            else:
                ret = return_message(
                    command,
                    errmfs.error(errmfs.COMPUTERNOTFOUND)
                ) #Computer not exists

            # WRAP THE RESULT OF COMMAND
            wrap(filename_return, ret)
            fp = open(filename_return, 'rb')
            ret = fp.read()
            fp.close()
            os.remove(filename_return)

            return HttpResponse(ret, mimetype='text/plain')

        # REGISTERS
        elif functs_register.has_key(command): # COMMAND NOT USE KEYS PAIR, ONLY USERNAME AND PASSWORD
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
                ret =  return_message(command, errmfs.error(errmfs.GENERIC))

            os.remove(filename)

            return HttpResponse(json.dumps(ret), mimetype='text/plain')

        # PACKAGER
        elif functs_packager.has_key(command):
            save_request_file(request.FILES[message], filename)

            # UNWRAP AND EXECUTE COMMAND
            data = unwrap(filename,"migasfree-packager")
            if data.has_key("errmfs"):
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

        else:
            return HttpResponse(
                return_message(
                    command,
                    str(errmfs.error(errmfs.COMMANDNOTFOUND))
                ),
                mimetype='text/plain'
            ) #Command not exists

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
        ret = '<?xml version="1.0" encoding="UTF-8" standalone= "yes"?>'+"\n"
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
            ret += "<"+e.prefix+">"
            ret += "`"+e.namefunction()+"`"
            ret += "</"+e.prefix+">"
        ret += "</ATTRIBUTES>"

        ret += "<FAULTS>"
        for e in faults:
            ret += "<"+e.name+">"
            ret += "`"+e.namefunction()+"`"
            ret += "</"+e.name+">"
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
    ret += "tooltip_status \""+ _("Creating Attributes and Faults") +"\"\n"
    ret += "_FILE_XML=\"$_DIR_TMP/update.xml\"\n"
    ret += "cat > $_FILE_XML << EOF\n"
    ret += creaxml(properties, faults) + "\n"
    ret += "EOF\n\n"
    ret += "echo 'Done'\n"

    ret += "# Upload an run update.xml\n"
    ret += "tooltip_status \""+ _("Uploading Attributes and Faults") +"\"\n"
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

            computer.history_sw = str(computer.history_sw) + unicode(destination.read(), "utf-8")
            computer.save()
            os.remove(filename)
            destination.close()
            ret = "OK"

        #SI RECIBIMOS UN FICHERO software.log
        if f.name == "software.log":
            grabar()
            destination = open(filename, 'rb')

            try:
                computer = Computer.objects.get(name=pc)
            except: #si no esta el Equipo lo añadimos
                computer = Computer(name=pc)
                computer.dateinput = t

            computer.software = unicode(destination.read(), "utf-8")
            computer.save()
            os.remove(filename)
            destination.close()
            ret = "OK"

        #SI RECIBIMOS UN FICHERO base.log
        if f.name == "base.log":
            grabar()
            destination = open(filename, 'rb')

            try:
                oversion = Version.objects.get(name=Computer.objects.get(name=pc).version)
            except: #si no esta el Equipo lo añadimos
                pass
            oversion.base = unicode(destination.read(), "utf-8")
            oversion.save()
            os.remove(filename)
            destination.close()
            ret = "OK"

        #SI RECIBIMOS UN FICHERO DIST.ERR
        if f.name == "migasfree.err":
            grabar()
            destination = open(filename, 'rb')
            try:
                computer = Computer.objects.get(name=pc)
            except: #si no esta el Equipo lo añadimos
                computer = Computer(name=pc)
                computer.dateinput = t
                computer.save()

            o_error = Error()
            o_error.computer = computer
            o_error.date = m
            o_error.error = unicode(destination.read(),"utf-8")
            o_error.save()
            os.remove(filename)
            destination.close()
            ret = "OK"

        #SI RECIBIMOS UN FICHERO install_device_param (Codigo de instalación de device)
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

        #SI RECIBIMOS UN FICHERO hardware.json (Inventario Hardware)
        if f.name == "hardware.json":
            grabar()

            try:
                computer = Computer.objects.get(name=pc)
            except: #si no esta el Equipo lo añadimos
                computer = Computer(name=pc)
                computer.dateinput = t
            computer.save()

            #process_hw(computer, filename)

            ret = "OK"
            os.remove(filename)


        #SI RECIBIMOS UN FICHERO net-devices.json
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
    return render_to_response(
        "info.html",
        {
            "title": "Create Repository Files.",
            "contentpage": html,
            "user": request.user,
            "root_path": "/migasfree/admin/"
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

        #we add the store
        try:
            o_store = Store.objects.get(name=store, version=oversion)
        except: #if not exists the Store, we add it
            o_store = Store()
            o_store.name = store
            o_store.version = oversion
            o_store.save()

        grabar()

        #we add the package
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


        #we add the store
        try:
            o_store = Store.objects.get(name=store, version=oversion)
        except: #if not exists the Store, we add it
            o_store = Store()
            o_store.name = store
            o_store.version = oversion
            o_store.save()

        #we add the Package/Set
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

def chart_selection(request, param):
    """
    Charts Menu of migasfree
    """

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/migasfree/login')

    return render_to_response(
        'chart_selection.html',
        {
            "title": _("Charts Menu"),
            "description": "",
            "user": request.user,
            "root_path": "/migasfree/admin/",
            "LANGUAGE_CODE": request.LANGUAGE_CODE
        }
    )

def chart(request, param):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/migasfree/login')

    filters = []
    filters.append(param)

    return render_to_response(
        'chart.html',
        {
            "user": request.user,
            "root_path": "/migasfree/admin/",
            "LANGUAGE_CODE": request.LANGUAGE_CODE
        }
    )

def hourly_updated(request, param):
    o_chart = Chart()
    timeformat = "%H h. %b %d "
    o_chart.title.text = _("Updated Computers / Hour")
    o_chart.title.style = "{font-size: 18px; color: #417690; text-align: center;}" # FIXME remove

    element1 = Chart()
    element1.values =  []
    labels = []

    y = 24 * 4 # 4 days
    delta = timedelta(hours = 1)
    n = datetime.now()-((y-25)*delta)
    n = datetime(n.year, n.month, n.day, 0)

    for i in range(y):
        value = Update.objects.filter(date__gte = n, date__lt = n+delta).values('computer').distinct().count()

        element1.values.append(value)
        element1.tip = "#x_label#    #val# "+_("Computers")

        labels.append(n.strftime(timeformat))
        n = n+delta

    element1.type = "bar"
#    element1.dot_style.type = "dot"
    element1.width = 2
    element1.colour = "#417690"
    element1.text = "" #Label
    element1.font_size = 10

    o_chart.x_axis.labels.stroke =  3
    o_chart.x_axis.labels.steps =  24
    o_chart.x_axis.labels.rotate =  270

    o_chart.x_axis.labels.labels = labels

    # y_axis
    o_chart.y_axis.max = max(element1.values)
    o_chart.y_axis.steps = 10**( len(str(o_chart.y_axis.max*4))-2)
    o_chart.y_axis.max = o_chart.y_axis.max + ( 10**( len(str(o_chart.y_axis.max*4))-2)/2)

    o_chart.elements = [element1,]
    o_chart.y_legend.text = _("Computers")
    o_chart.y_legend.style = "{font-size: 12px; color: #778877}"
    o_chart.x_legend.text = _("Hour")
    o_chart.x_legend.style = "{font-size: 12px; color: #778877}"

    return HttpResponse(o_chart.create(), mimetype="text/plain")

def daily_updated(request, param):
    o_chart = Chart()
    timeformat = "%b %d"
    o_chart.title.text = _("Updated Computers / Day")
    o_chart.title.style = "{font-size: 18px; color: #417690; text-align: center;}" # FIXME remove

    element1 = Chart()
    element1.values =  []
    labels = []

    days = 35
    delta = timedelta(days = 1)
    n = date.today()-((days-1)*delta)
    for i in range(days):
        value = Update.objects.filter(date__gte = n, date__lt = n+delta).values('computer').distinct().count()
        element1.values.append(value)
        element1.tip = "#x_label#    #val# "+_("Computers")
        labels.append(n.strftime(timeformat))
        n = n+delta

    element1.type = "bar"
    element1.dot_style.type = "dot"
    element1.width = 2
    element1.colour = "#417690"
    element1.text = "" #Label
    element1.font_size = 10

    o_chart.x_axis.labels.rotate =  270
    o_chart.x_axis.labels.labels = labels

    # y_axis
    o_chart.y_axis.max = max(element1.values)
    o_chart.y_axis.steps = 10**( len(str(o_chart.y_axis.max*4))-2)
    o_chart.y_axis.max = o_chart.y_axis.max + ( 10**( len(str(o_chart.y_axis.max*4))-2)/2)

    o_chart.elements = [element1,]

    o_chart.y_legend.text = _("Computers")
    o_chart.y_legend.style = "{font-size: 12px; color: #778877}"
    o_chart.x_legend.text = _("Day")
    o_chart.x_legend.style = "{font-size: 12px; color: #778877}"

    return HttpResponse(o_chart.create(), mimetype="text/plain")

def monthly_updated(request, param):
    o_chart = Chart()
    timeformat = "%b"
    o_chart.title.text = _("Updated Computers / Month")
    o_chart.title.style = "{font-size: 18px; color: #417690; text-align: center;}" # FIXME remove

    element1 = Chart()
    element1.values = []
    labels = []

    year= int(date.today().strftime("%Y"))
    years = [year-1, year]
    months = []
    for i in range(1, 13):
        months.append(date(year, i, 1).strftime(timeformat))

    for y in years:
        for m in range(1, 13):
            value = Update.objects.filter(date__month = m, date__year = y).values('computer').distinct().count()
            element1.values.append(value)
            element1.tip = "#x_label#    #val# "+_("Computers")
            labels.append(str(months[m-1]) +" " +str(y))

    element1.type = "bar"
    element1.dot_style.type = "dot"
    element1.width = 2
    element1.colour = "#417690"
    element1.text = "" #Label
    element1.font_size = 10

    o_chart.x_axis.labels.rotate =  270
    o_chart.x_axis.labels.labels = labels

    # y_axis
    o_chart.y_axis.max = max(element1.values)
    o_chart.y_axis.steps = 10**( len(str(o_chart.y_axis.max*4))-2)
    o_chart.y_axis.max = o_chart.y_axis.max + ( 10**( len(str(o_chart.y_axis.max*4))-2)/2)

    o_chart.elements = [element1,]

    o_chart.y_legend.text = _("Computers")
    o_chart.y_legend.style = "{font-size: 12px; color: #778877}"
    o_chart.x_legend.text = _("Month")
    o_chart.x_legend.style = "{font-size: 12px; color: #778877}"

    return HttpResponse(o_chart.create(), mimetype="text/plain")

def delay_schedule(request, param):
    o_chart = Chart()
    o_chart.title.text = _("Provided Computers / Delay")
    o_chart.title.style = "{font-size: 18px; color: #417690; text-align: center;}" # FIXME remove

    o_chart.elements = []
    o_schedules = Schedule.objects.all()
#    lines = []
    colours = ["#fa6900", "#417690", "#C4D318", "#FF00FF", "00FFFF", "#50284A", "#7D7B6A",]
    c = 0
    m = 0
    for sched in o_schedules:
        lst_attributes = []
        line = Chart()
        line.type = "line"
        line.dot_style.type = "dot"
        line.width = 2
        line.colour = colours[c]
        c = c+1
        if c == len(colours):
            c = 0

        line.font_size = 10

        line.values = []
        delays = ScheduleDelay.objects.filter(schedule__name=sched.name).order_by("delay")
        d = 1
        value = 0
        for delay in delays:
            for i in range(d, delay.delay):
                line.values.append(value)
            for att in delay.attributes.all():
                lst_attributes.append(att.id)
            value = Login.objects.filter(Q(attributes__id__in=lst_attributes)).values('computer_id').annotate(lastdate=Max('date')).count()
            print lst_attributes
            d = delay.delay
        line.values.append(value)
        line.text = sched.name
        line.tip = "#x_label# " + _("days") + " #val# "+_("Computers")

        m = max(m, max(line.values))
        o_chart.elements.append(line)

    o_chart.y_axis.max = m
    o_chart.y_axis.steps = 10**( len(str(o_chart.y_axis.max*4))-2)
    o_chart.y_axis.max = o_chart.y_axis.max + ( 10**( len(str(o_chart.y_axis.max*4))-2)/2)

    o_chart.y_legend.text = _("Computers")
    o_chart.y_legend.style = "{font-size: 12px; color: #778877}"
    o_chart.x_legend.text = _("Delay")
    o_chart.x_legend.style = "{font-size: 12px; color: #778877}"

    return HttpResponse(o_chart.create(), mimetype="text/plain")

def version_computer(request, param):
    o_chart = Chart()
    o_chart.title.text = _("Computers / Version")
    o_chart.title.style = "{font-size: 18px; color: #417690; text-align: center;}" # FIXME remove

    qry = Computer.objects.values("version__name").annotate(count=Count("id"))
    element1 = Chart()
    element1.type = "pie"
    element1.alpha = 0.6
    element1.start_angle = 35
    element1.animate = [{"type": "fade"}, {"type": "bounce", "distance": 10}]
    element1.tip = "#val# "+_("of")+" #total#<br>#percent#"
    element1.colours = ["#1C9E05", "#FF368D"]
    element1.gradient_fill = True
    element1.radius = 100
    element1.values = []
    for e in qry:
#       element1.values = [2000, 3000, 4000, {"value": 6000.511, "label": "hello (6000.51)", "on-click": "http://example.com"}]
        element1.values.append(
            {
                "value": e.get("count"),
                "label": e.get("version__name")
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

    return render_to_response(
        'hardware.html',
        {
            "title": computer.name,
            "computer": computer,
            "description": _("Hardware Information"),
            "query": qry,
            "user": request.user,
            "root_path": "/migasfree/hardware/"
        }
    )

@login_required
def hardware_resume(request, param):
    qry = HwNode.objects.filter(Q(computer__id=param)).order_by("id")
    if qry.count > 0:
        computer = qry[0].computer

    return render_to_response(
        'hardware_resume.html',
        {
            "title": computer.name,
            "computer": computer,
            "description": _("Hardware Information"),
            "query": qry,
            "user": request.user,
            "root_path": "/migasfree/hardware/"
        }
    )

# ---- query.py ----

def query2(request, parameters, form_param):
    o_query = Query.objects.get(id=parameters["id_query"])

    version = parameters["user_version"]   #pylint: disable-msg=W0612

    # execute query
    try:
        exec(o_query.code.replace("\r", ""))

        if vars().has_key("fields") == False:
            fields = []
            for k, v in query.values()[0].iteritems():
                v = v #for pylint
                fields.append(k)

        if vars().has_key("titles") == False:
            titles = fields

        vl_fields = []

        for o in query:
            o = o #for pylint
            cols = []
            for f in fields:
                cols.append(eval("o.%s" % f))
            vl_fields.append(cols)

        filters = []
        for x in form_param:
            if not (x.name == "id_query" or x.name == "user_version"):
                filters.append(str(x.label) + ": " + parameters[x.name + "_display"])

        return render_to_response(
            'query.html',
            {
                "title": o_query.name,
                "description": o_query.description,
                "titles": titles,
                "query": vl_fields,
                "filters": filters,
                "row_count": query.count(),
                "user": request.user,
                "root_path": "/migasfree/admin/"
            }
        )
    except:
        return HttpResponse(
            "Error in field 'code' of query:\n" + str(sys.exc_info()),
            mimetype="text/plain"
        )

@login_required
def query(request, param):
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
                    parameters[x.name + "_display"] = option_description(str(x), parameters[x.name])

                return query2(request, parameters, g_form_param)
            except:
                return HttpResponse(
                    "Error in field 'parameters' of query:\n" + str(sys.exc_info()[1]),
                    mimetype="text/plain"
                )

    # show parameters form
    o_query = Query.objects.get(id=request.GET.get('id', ''))
    dic_initial = {
        'id_query': request.GET.get('id', ''),
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

            return render_to_response(
                'parameters.html',
                {
                    'form': g_form_param,
                    'title': _("Parameters for Query: %s") % o_query.name,
                    "user": request.user,
                    "root_path": "/migasfree/admin/"
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
        fileremote = "http://$MIGASFREE_SERVER/repo/" + str(o_device.model.devicefile.name)
        filelocal = "/tmp/migasfree/" + str(o_device.model.devicefile.name)

        ret = ". /usr/share/migasfree/init\n"

        #PARAMS
        ret = ret+"_NAME="+name_printer(o_device.model.manufacturer.name, o_device.model.name, o_device.name)+"\n"

#        ret = ret+"_NAME="+o_device.name+"_"+device.model.name+"\n"
        ret = ret+o_device.values+"\n"

        #Download device file
        ret = ret+"mkdir -p /tmp/migasfree/devices\n"
        ret = ret+"if [ \"$MIGASFREE_PROXY\"=\"\" ]; then\n"
        ret = ret+"    wget --no-cache --no-proxy --header=\"Accept: text/plain;q=0.8\" --header=\"Accept-Language: $MIGASFREE_LANGUAGE\" -dnv \""+fileremote+"\" -O "+filelocal+" 2>/dev/null\n"
        ret = ret+"else\n"
        ret = ret+"    http_proxy=$MIGASFREE_PROXY\n"
        ret = ret+"    wget --no-cache --header=\"Accept: text/plain;q=0.8\" --header=\"Accept-Language: $MIGASFREE_LANGUAGE\" -dnv \""+fileremote+"\" -O "+filelocal+" 2>/dev/null\n"
        ret = ret+"fi\n\n"

        #Execute code to add printer
        ret = ret+o_device.render_install()
        #Delete device file
        ret = ret+"rm "+filelocal+"\n"

        # Add the device to computer
        try:
            o_computer = Computer.objects.get(name=pc)
        except: #si no esta el Equipo lo añadimos
            o_computer = Computer(name=pc)
            o_computer.version = Version.objects.get(id=1)
            o_computer.dateinput = t
            o_computer.save()

        o_computer.devices.add(o_device.id)
        o_computer.save()

        return ret

    def selection(number, title, options):
        if (len(options) <= 1) and (title == "TYPE" or title == "PORT"):
            ret = "_"+title+"=\""+options[0]+"\"\n"
        else:
            ret = "dialog --backtitle \"migasfree - INSTALL DEVICE " + number + "\" --menu \""+ title +"\" 0 0 0"

            i = 0
            for o in options:
                ret = ret+" \""+str(i)+"\" \""+o+"\""
                i += 1

            ret = ret+" 2>/tmp/ans\n"
            ret = ret+"#CANCEL\n"
            ret = ret+"if [ $? = 1 ]\n then\n"
            ret = ret+"   rm -f /tmp/ans\n"
            ret = ret+"   clear\n"
            ret = ret+"   exit 0\n"
            ret = ret+"fi\n"
            ret = ret+"_OPCION=\"`cat /tmp/ans`\"\n"
            ret = ret+"clear\n"

            i = 0
            for o in options:
                ret = ret+"if [ $_OPCION = \""+str(i)+"\" ] \n  then\n"
                ret = ret+"_"+title+"=\""+o+"\"\n"
                ret = ret+"fi\n"
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
        manufacturers = DeviceManufacturer.objects.filter(devicemodel__devicetype__name=devicetype).distinct()
        for o in manufacturers:
            l.append(o.name)

        return l

    def list_model(devicetype, manufacturer):
        l = []
        o_models = DeviceModel.objects.filter(devicetype__name=devicetype , manufacturer__name=manufacturer)
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
        ret = ret+"#whatmodel\n"
        ret = ret+". /usr/share/migasfree/init\n"
        ret = ret+"_FILE_MIGAS=/tmp/install_device_type\n"
        ret = ret+"chmod 700 $_FILE_MIGAS\n"
        ret = ret+"_NUMBER="+number+"\n"
        ret = ret+selection(number, "TYPE", list_type() )
        ret = ret+"download_file \"device/?CMD=install&HOST=$HOSTNAME&TYPE=$_TYPE&NUMBER=$_NUMBER\" \"$_FILE_MIGAS\"\n"

        ret = ret+"if [ $? == 0 ]\n  then\n"
        ret = ret+"   chmod 700 $_FILE_MIGAS\n"
        ret = ret+"   $_FILE_MIGAS\n"
        ret = ret+"fi\n"

        return ret

    def whatdevicemanufacturer(number, devicetype):
        ret = "#!/bin/bash\n"
        ret = ret+"#whatmanufacturer\n"
        ret = ret+". /usr/share/migasfree/init\n"
        ret = ret+"_FILE_MIGAS=/tmp/install_device_manufacturer\n"
        ret = ret+"chmod 700 $_FILE_MIGAS\n"
        ret = ret+"_NUMBER="+number+"\n"
        ret = ret+"_TYPE="+devicetype+"\n"
        ret = ret+selection(number, "MANUFACTURER", list_manufacturer(devicetype) )
        ret = ret+"download_file \"device/?CMD=install&HOST=$HOSTNAME&MANUFACTURER=$_MANUFACTURER&TYPE=$_TYPE&NUMBER=$_NUMBER\"  \"$_FILE_MIGAS\"\n"

        ret = ret+"if [ $? == 0 ]\n  then\n"
        ret = ret+"   chmod 700 $_FILE_MIGAS\n"
        ret = ret+"   $_FILE_MIGAS\n"
        ret = ret+"fi\n"

        return ret

    def whatmodel(number, devicetype, manufacturer):
        ret = "#!/bin/bash\n"
        ret = ret+"#whatmodel\n"
        ret = ret+". /usr/share/migasfree/init\n"
        ret = ret+"_FILE_MIGAS=/tmp/install_device_model\n"
        ret = ret+"chmod 700 $_FILE_MIGAS\n"
        ret = ret+"_NUMBER="+number+"\n"
        ret = ret+"_TYPE="+devicetype+"\n"
        ret = ret+"_MANUFACTURER="+manufacturer+"\n"
        ret = ret+selection(number, "MODEL", list_model(devicetype, manufacturer) )
        ret = ret+"download_file \"device/?CMD=install&HOST=$HOSTNAME&MODEL=$_MODEL&MANUFACTURER=$_MANUFACTURER&TYPE=$_TYPE&NUMBER=$_NUMBER\" \"$_FILE_MIGAS\"\n"

        ret = ret+"if [ $? == 0 ]\n  then\n"
        ret = ret+"   chmod 700 $_FILE_MIGAS\n"
        ret = ret+"   $_FILE_MIGAS\n"
        ret = ret+"fi\n"

        return ret

    def whatport(number, devicetype, manufacturer, model):
        ret = "#!/bin/bash\n"
        ret = ret+"#whatport\n"
        ret = ret+". /usr/share/migasfree/init\n"
        ret = ret+"_FILE_MIGAS=/tmp/install_device_port\n"
        ret = ret+"chmod 700 $_FILE_MIGAS\n"
        ret = ret+"_NUMBER="+number+"\n"
        ret = ret+"_TYPE="+devicetype+"\n"
        ret = ret+"_MANUFACTURER="+manufacturer+"\n"
        ret = ret+"_MODEL="+model+"\n"
        ret = ret+selection(number, "PORT", list_port(model))
        ret = ret+"download_file \"device/?CMD=install&HOST=$HOSTNAME&MODEL=$_MODEL&MANUFACTURER=$_MANUFACTURER&TYPE=$_TYPE&NUMBER=$_NUMBER&PORT=$_PORT\" \"$_FILE_MIGAS\"\n"

        ret = ret+"if [ $? == 0 ]\n then\n"
        ret = ret+"   chmod 700 $_FILE_MIGAS\n"
        ret = ret+"   $_FILE_MIGAS\n"
        ret = ret+"fi\n"

        return ret

    def processmodel(number, devicetype, manufacturer, model, port):
        ret = "#!/bin/bash\n"
        ret = ret+"#processmodel\n"
        ret = ret+". /usr/share/migasfree/init\n"
        ret = ret+"_FILE_MIGAS=/tmp/install_device_code\n"
        ret = ret+"_FILE_MIGAS_PARAM=/tmp/install_device_param\n"
        ret = ret+"_FILE_RESP=/tmp/resp\n"

        o_devicemodel = DeviceModel.objects.get(name=model)
        o_deviceconnection = DeviceConnection.objects.get(name=port, devicetype__name=devicetype)

        fields = o_deviceconnection.fields.split()
        ret = ret+"rm -f $_FILE_MIGAS_PARAM\n"

        ret = ret+"_NAME='"+name_printer(manufacturer, model, number)+"'\n"
        ret = ret+"echo ""_NAME='"+name_printer(manufacturer, model, number)+"'"" >>$_FILE_MIGAS_PARAM\n"
        for f in fields:
            ret = ret+"dialog --backtitle \"migasfree - INSTALL DEVICE "+number+"\" --inputbox \""+f+"\" 0 0 2>/tmp/ans\n"
            ret = ret+"#CANCEL\n"
            ret = ret+"if [ $? = 1 ]\n  then\n"
            ret = ret+"  rm -f /tmp/ans\n"
            ret = ret+"  clear\n"
            ret = ret+"  exit 0\n"
            ret = ret+"fi\n"
            ret = ret+"_"+f+"=\"`cat /tmp/ans`\"\n"
            ret = ret+"echo \"_"+f+"=\'$_"+f+"\'\" >>$_FILE_MIGAS_PARAM\n"

        #We add the device
        o_device = Device()
        o_device.name = number
        o_device.model = o_devicemodel
        o_device.connection = o_deviceconnection
        o_device.save()

        #Actualize the device
        ret = ret+"upload_file \"$_FILE_MIGAS_PARAM\" directupload/ \"PC=$HOSTNAME;TYPE="+devicetype+";NUMBER="+number+";MODEL="+model+";PORT="+port+"\"\n"

        ret = ret+"cat > $_FILE_MIGAS << EOF \n"
        ret = ret+". $_FILE_MIGAS_PARAM\n"
        ret = ret+downfiledevice(host, number, port)+"\n"
        ret = ret+"EOF\n"
        ret = ret+"chmod 700 $_FILE_MIGAS\n"
        ret = ret+"$_FILE_MIGAS\n"

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
                ret = ret+downfiledevice(host, c.name, c.connection.name)

            return HttpResponse(ret, mimetype="text/plain")

        if port == "":
            cursor = Device.objects.filter(name=number)
        else:
            cursor = Device.objects.filter(name=number, connection__name=port)
            if len(cursor) == 1:
                ret = downfiledevice(host, number, port)

                return HttpResponse(ret, mimetype="text/plain")

        if len(cursor) > 0 : # Si se ha configurado alguna vez el dispositivo
            model = cursor[0].model.name
            deviceconnection = DeviceConnection.objects.filter(devicemodel__name=model)
            if len(deviceconnection) == 1 : #SI el modelo tiene 1 conexion
                ret = downfiledevice(host, number, deviceconnection[0].name)
                return HttpResponse(ret, mimetype = "text/plain")
            else: #SI el modelo no tiene 1 conexion
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
            if devicetype == "" :
                ret = whatdevicetype(number)
                return HttpResponse(ret, mimetype="text/plain")

            # Pedimos el fabricante
            if manufacturer == "" :
                ret = whatdevicemanufacturer(number, devicetype)
                return HttpResponse(ret, mimetype="text/plain")

            # Pedimos el modelo
            if model == "" :
                ret = whatmodel(number, devicetype, manufacturer)
                return HttpResponse(ret, mimetype="text/plain")

            # Pedimos el puerto
            if port == "" :
                ret = whatport(number, devicetype, manufacturer, model)
                return HttpResponse(ret, mimetype="text/plain")

            else:
                #Devolvemos el script para la instalacion
                ret = processmodel(number, devicetype, manufacturer, model, port)

                return HttpResponse(ret, mimetype="text/plain")
