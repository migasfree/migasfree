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
from migasfree.server.load_devices import load_devices


def softwarebase(request):
    version = request.GET.get('VERSION', '')
    try:
        ret = Version.objects.get(name=version).base
    except:
        ret = ""

    return HttpResponse(ret, mimetype="text/plain")


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
def createrepositories(request):
    """
    Create the files of Repositories in the server
    """
    try:
        version = UserProfile.objects.get(id=request.user.id).version
    except:
        return HttpResponse(
            _('No version to find info.'),
            mimetype="text/plain"
        )  # FIXME

    return render(
        request,
        "info.html",
        {
            "title": _("Create Repositories"),
            "contentpage": create_repositories(version.id),
        }
    )


def createrepositoriesofpackage(request, param):
    if request.method != 'GET':
        return HttpResponse("ERROR", mimetype='text/plain')

    user = auth.authenticate(
        username=request.GET.get('username'),
        password=request.GET.get('password')
    )
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

        return "OK"

    if request.method == 'POST':
        # Other data on the request.FILES dictionary:
        #   filesize = len(file['content'])
        #   filetype = file['content-type']

        user = auth.authenticate(
            username=request.COOKIES.get('username'),
            password=request.COOKIES.get('password')
        )
        if user is None:
            return HttpResponse(
                "ERROR. User no authenticated.",
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

        return "OK"

    if request.method == 'POST':
        # Other data on the request.FILES dictionary:
        #   filesize = len(file['content'])
        #   filetype = file['content-type']

        user = auth.authenticate(
            username=request.COOKIES.get('username'),
            password=request.COOKIES.get('password')
        )
        if user is None:
            return HttpResponse(
                "ERROR. User no authenticated.",
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
