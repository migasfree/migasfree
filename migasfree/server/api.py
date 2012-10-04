# -*- coding: utf-8 -*-

import os
import jsontemplate
import time
import inspect
from datetime import datetime

from django.db.models import Q
from django.contrib import auth

from migasfree.settings import MIGASFREE_REPO_DIR


from migasfree.server.models import *
from migasfree.server.logic import *
from migasfree.server.errmfs import *
from migasfree.server.functions import *
from migasfree.server.security import *

def upload_computer_hardware(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        o_computer = Computer.objects.get(name=computer)
        HwNode.objects.filter(computer=o_computer).delete()
        load_hw(o_computer, data[cmd], None, 1)
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret

def upload_computer_software_base_diff(request, computer, data): #pylint: disable-msg=C0103
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        o_computer = Computer.objects.get(name=computer)
        o_computer.software = data[cmd]
        o_computer.save()
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret

def upload_computer_software_base(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        o_version = Version.objects.get(name=Computer.objects.get(name=computer).version)
        o_version.base = data[cmd]
        o_version.save()
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret

def upload_computer_software_history(request, computer, data): #pylint: disable-msg=C0103
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        o_computer = Computer.objects.get(name=computer)
        o_computer.history_sw = str(o_computer.history_sw)+"\n\n"+data[cmd]
        o_computer.save()
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret

def get_computer_software(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        o_computer = Computer.objects.get(name=computer)
        ret = return_message(cmd, Version.objects.get(name=o_computer.version).base)
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret

def upload_computer_errors(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    m = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        o_computer = Computer.objects.get(name=computer)
        o_error = Error()
        o_error.computer = o_computer
        o_error.date = m
        o_error.error = data[cmd]
        o_error.save()
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret

def upload_computer_message(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    m = time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        o_computer = Computer.objects.get(name=computer)
    except:
        return return_message(cmd, error(COMPUTERNOTFOUND))

    try:
        try:
            o_message = Message.objects.get(computer=o_computer)
            if data[cmd] == "":
                o_message.delete()
                Update(computer=o_computer, date=m).save()
                return return_message(cmd, ok())
        except:
            o_message = Message(computer=o_computer)

        o_message.text = data[cmd]
        o_message.date = m
        o_message.save()
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret

def return_message(cmd, data):
    return {'%s.return' % cmd: data}

def get_properties(request, computer, data):
    """
        First call of client requesting to server what he must do. The server responds with a string json with structure :

        OUTPUT:
        ======
            { "properties": [ {"prefix":"PREFIX", "function":"CODE" , "language": "LANGUAGE"} ,...] ,
               }

        The client will eval the "functions" in  PROPERTIES and FAULTS and will upload it to server in a file called request.json
        calling to "post_request" view
    """
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    properties = []

    try:
        # All active properties
        for e in Property.objects.filter(active=True):
            properties.append({
                "language": LANGUAGES_CHOICES[e.language][1],
                "name": e.prefix,
                "code": e.code
            })

        ret = return_message(cmd, {"properties":properties})

    except:
        ret = return_message(cmd, error(GENERIC))

    return ret

# process the file request.json and return a string json with the faultsdef, repositories, packages and devices
def upload_computer_info(request, computer, data):
    """
        INPUT:
        =====
        A file "request.json" with the result of evaluate the request obtained by "get_regest"

            {
              "computer":{"hostname":HOSTNAME,"ip":IP,"version":VERSION,"user":USER,"user_fullname":USER_FULLNAME},
              "attributes":[{"name":VALUE},...]
            {

        OUTPUT:
        ======
        After of process this file the server respond to client with a string json with:

            { "faultsdef": [{"name":"NAME", "function":"CODE" , "language": "LANGUAGE"} ,...] ,
              "repositories" : [ {"name": "REPONAME" }, ...] ,
              "packages": {"install": ["pck1","pck2","pck3",...], "remove": ["pck1","pck2","pck3",...]} ,
              "base": true/false ,
              "devices": {"install": bashcode , "remove": bashcode} #TODO move code to client

    """

    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    t = time.strftime("%Y-%m-%d")
    m = time.strftime("%Y-%m-%d %H:%M:%S")

    lst_attributes = [] # List of attributes of computer

    ret = ""

    try:
        dic_computer = data.get("upload_computer_info").get("computer")
        properties = data.get("upload_computer_info").get("attributes")

        # 1.- PROCESS COMPUTER
        if dic_computer["hostname"] == "desktop":
            str_error = trans('desktop is not valid name for this computer: IP=%(ip)s') % {'ip': dic_computer["ip"]}
            o_error = Error()
            o_error.computer = Computer.objects.get(name="desktop")
            o_error.date = m
            o_error.error = str_error
            o_error.save()

            return return_message(cmd, error(COMPUTERNOTFOUND))

        #registration of ip and version of computer
        try:
            o_computer = Computer.objects.get(name=dic_computer["hostname"])
            o_computer.ip = dic_computer["ip"]
            o_computer.version = Version.objects.get(name=dic_computer["version"])
            o_computer.save()
        except: # if not exists the computer, we add it
            o_computer = Computer(name=dic_computer["hostname"])
            o_computer.dateinput = t
            o_computer.ip = dic_computer["ip"]
            o_computer.version = Version.objects.get(name=dic_computer["version"])
            o_computer.save()

        # if not exists the user, we add it
        try:
            o_user = User.objects.get(name=dic_computer["user"])
        except:
            o_user = User()
            o_user.name = dic_computer["user"]
            try:
                o_user.fullname = dic_computer["user_fullname"]
            except:
                o_user.fullname = ""
            o_user.save()

        # Save Login
        save_login(dic_computer["hostname"], dic_computer["user"])
        o_login = Login.objects.get(computer=Computer.objects.get(name=dic_computer["hostname"]), user=User.objects.get(name=dic_computer["user"]))
        o_login.attributes.clear()

        # Get version
        version = dic_computer["version"]

        o_version = Version.objects.get(name=version)

        # Get the Package Management System
#        o_pms = Pms.objects.get(id=o_version.pms.id)

        # 2.- PROCESS PROPERTIES
        for e in properties:
            o_property = Property.objects.get(prefix=e)
            value = properties.get(e)
            try:
                # we execute the before_insert function
                if o_property.before_insert != "":
                    exec(o_property.before_insert.replace("\r",""))

                # NORMAL
                if o_property.kind == "N":
                    lst_attributes.append(new_attribute(o_login, o_property, value))

                # LIST
                if o_property.kind == "-":
                    mylist = value.split(",")
                    for element in mylist:
                        lst_attributes.append(new_attribute(o_login, o_property, element))

                # ADDS RIGHT
                if o_property.kind == "R":
                    lista = value.split(".")
                    c = value
                    l = 0
                    for x in lista:
                        lst_attributes.append(new_attribute(o_login, o_property, c[l:]))
                        l = l+len(x)+1


                # ADDS LEFT
                if o_property.kind == "L":
                    lista = value.split(".")
                    c = value
                    l = 0
                    for x in lista:
                        l = l+len(x)+1
                        lst_attributes.append(new_attribute(o_login, o_property, c[0:l-1]))

                # we execute the after_insert function
                if o_property.after_insert != "":
                    exec(o_property.after_insert.replace("\r",""))

            except:
                pass

        # 3 FaultsDef
        lst_faultsdef = []
        faultsdef = FaultDef.objects.filter(Q(attributes__id__in=lst_attributes))
        faultsdef = faultsdef.filter(Q(active=True))
        for d in faultsdef:
            lst_faultsdef.append({"language":LANGUAGES_CHOICES[d.language][1], "name":d.name, "code":d.code})

        dic_repos = {}

        repositories = Repository.objects.filter(Q(attributes__id__in=lst_attributes), Q(version__id=o_version.id))
        repositories = repositories.filter(Q(version__id=o_version.id), Q(active=True))

        for r in repositories:
            dic_repos[r.name] = r.id

        repositories = Repository.objects.filter(Q(schedule__scheduledelay__attributes__id__in=lst_attributes), Q(active=True))
        repositories = repositories.filter(Q(version__id=o_version.id), Q(active=True))
        repositories = repositories.extra(select={'delay': "server_scheduledelay.delay",})

        for r in repositories:
            if horizon(r.date, r.delay) <= datetime.now().date():
                dic_repos[r.name] = r.id

        repositories = Repository.objects.filter(Q(id__in=dic_repos.values()) )

        #FILTER EXCLUDED ATTRIBUTES
        repositories = repositories.filter(~Q(excludes__id__in=lst_exclude))

        #4.- CREATE JSON
        lst_repos = []
        lst_pkg_remove = []
        lst_pkg_install = []

        for r in repositories:
            lst_repos.append({"name": r.name})
            for p in r.toremove.replace("\n"," ").split(" "):
                if p != "":
                    lst_pkg_remove.append(p)
            for p in r.toinstall.replace("\n"," ").split(" "):
                if p != "":
                    lst_pkg_install.append(p)

        #DEVICES
        lst_dev_remove = []
        lst_dev_install = []
        chk_devices = Mmcheck(o_computer.devices, o_computer.devices_copy)
        if chk_devices.changed() == True or o_computer.devices_modified == True:

            #remove the devices
            lst_diff = list_difference(s2l(o_computer.devices_copy), s2l(chk_devices.mms()))
            for d in lst_diff:
                try:
                    device = Device.objects.get(id=d)
                    lst_dev_remove.append(device.fullname())
                except:
                    pass

            for device in o_computer.devices.all():
                lst_dev_install.append(device.fullname())

            o_computer.devices_copy = chk_devices.mms()
            o_computer.devices_modified = False
            o_computer.save()


        retdata = {}
        retdata["faultsdef"] = lst_faultsdef
        retdata["repositories"] = lst_repos
        retdata["packages"] = {"remove": lst_pkg_remove , "install": lst_pkg_install}
        retdata["devices"] = {"remove":lst_dev_remove, "install":lst_dev_install}
        retdata["base"] = (o_version.computerbase == o_computer.name)


        ret = return_message(cmd, retdata)
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret

def upload_computer_faults(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    faults = data.get(cmd).get("faults")
    o_computer = Computer.objects.get(name=computer)
    m = time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        # PROCESS FAULTS
        for e in faults:
            o_faultdef = FaultDef.objects.get(name=e)
            try:
                msg = faults.get(e)
                if msg <> "":
                    # we add the fault
                    o_fault = Fault()
                    o_fault.computer = o_computer
                    o_fault.date = m
                    o_fault.text = msg
                    o_fault.faultdef = o_faultdef
                    o_fault.save()
            except:
                pass

        retdata = {}

        ret = return_message(cmd, retdata)

    except:
        ret = return_message(cmd, error(GENERIC))

    return ret



#DEVICES

def get_device(request, computer, data):
    """
    return DeviceModel data for lpadmin
    """
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    d = data[cmd]
    try:
        o_device = Device.objects.get(name=d["NUMBER"])
        return return_message(cmd, o_device.data())
    except:
        return return_message(cmd, error(DEVICENOTFOUND))


def get_assist_devices(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        types = {}
        for dev_type in DeviceType.objects.all():
            manufacters = {}
            for dev_model_man in DeviceModel.objects.filter(devicetype__id=dev_type.id).distinct():
                models = {}

                for dev_model in DeviceModel.objects.filter(manufacturer__id=dev_model_man.manufacturer.id):
                    ports = {}

                    for dev_port in dev_model.connections.all():
                        parameters = {}

                        for token_type, token in jsontemplate._Tokenize(dev_port.uri, '{','}'):
                            if token_type == 1:
                                parameters[token] = {"default":""}

                        parameters["LOCATION"] = {"default":""}
                        parameters["INFORMATION"] = {"default":""}
                        parameters["ALIAS"] = {"default":""}

                        ports[dev_port.name] = {"type":"inputbox", "name":"PARAMETER", "value":parameters}
                    models[dev_model.name] = {"type":"menu", "name":"PORT", "value":ports}
                manufacters[dev_model_man.manufacturer.name] = {"type":"menu", "name":"MODEL", "value":models}
            types[dev_type.name] = {"type":"menu", "name":"MANUFACTURER", "value":manufacters}
        ret = return_message(cmd, {"type":"menu", "name":"TYPE", "value":types})
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret

def remove_device(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    d = data[cmd]
    try:
        o_device = Device.objects.get(name=d["NUMBER"])
        try:
            o_device.computer_set.remove(Computer.objects.get(name=computer))
            o_device.save()
            list_computers = []
            for c in o_device.computer_set.all():
                list_computers.append(c.name)
            return return_message(cmd, {"NUMBER":o_device.name, "COMPUTERS":list_computers})
        except:
            return return_message(cmd, error(GENERIC))
    except: #if not exist device
        return return_message(cmd, error(DEVICENOTFOUND))

def install_device(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    d = data[cmd]

    try:
        o_device = Device.objects.get(name=d["NUMBER"])
    except: #if not exist device
        try:
            o_device = Device()
            o_device.name = d["NUMBER"]
            o_device.alias = d["ALIAS"]
            o_devicemodel = DeviceModel.objects.get(name=d["MODEL"])
            o_device.model = o_devicemodel

            o_devicetype = DeviceType.objects.get(name=d["TYPE"])
            o_deviceconnection = DeviceConnection.objects.get(name=d["PORT"], devicetype=o_devicetype)
            o_device.connection = o_deviceconnection

            #evaluate uri
            o_device.uri = jsontemplate.expand(o_deviceconnection.uri, d)

            o_device.location = d["LOCATION"]
            o_device.information = d["INFORMATION"]
            o_device.save()

        except:
            return return_message(cmd, error(GENERIC))

    o_device.computer_set.add(Computer.objects.get(name=computer))
    o_device.save()
    list_computers = []
    for c in o_device.computer_set.all():
        list_computers.append(c.name)

    return return_message(cmd, {"NUMBER":o_device.name, "COMPUTERS":list_computers})

def register_computer(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    # REGISTER COMPUTER
    # Check Version
    if Version.objects.filter(name=data['version']):
        o_version = Version.objects.get(name=data['version'])
        # if not autoregister, check that the user can save computer
        if not o_version.autoregister:
            user = auth.authenticate(username=data['username'], password=data['password'])
            if not user or not user.has_perm("server.can_save_computer"):
                return return_message(cmd, error(CANNOTREGISTER))

        # ALL IS OK
        # 1.- Add Computer
        try:
            o_computer = Computer.objects.get(name=computer)
        except:
            o_computer = Computer(name=computer)
            o_computer.dateinput = time.strftime("%Y-%m-%d")
        o_computer.version = o_version
        o_computer.save()

        # 2.- returns keys to client
        ret = return_message(cmd, get_keys_to_client(data['version']))
    else:
        ret = return_message(cmd, error(VERSIONNOTFOUND))

    return ret

def get_key_packager(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    user = auth.authenticate(
        username=data['username'],
        password=data['password']
    )
    if not user.has_perm("server.can_save_package"):
        ret = return_message(cmd, error(CANNOTREGISTER))
    else:
        ret = return_message(cmd, get_keys_to_packager())

    return ret

def upload_server_package(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    f = request.FILES["package"]
    filename = os.path.join(
        MIGASFREE_REPO_DIR,
        data['version'],
        'STORES',
        data['store'],
        f.name
    )

    try:
        if Version.objects.filter(name=data['version']):
            o_version = Version.objects.get(name=data['version'])
        else:
            return return_message(cmd, error(VERSIONNOTFOUND))

        if Store.objects.filter(name=data['store'], version=o_version):
            o_store = Store.objects.get(name=data['store'], version=o_version)
        else:
            o_store = Store()
            o_store.name = data['store']
            o_store.version = o_version
            o_store.save()

        save_request_file(f, filename)

        #we add the package
        if not data['source']:
            if Package.objects.filter(name=f.name, version=o_version):
                o_package = Package.objects.get(name=f.name, version=o_version)
            else:
                o_package = Package(name=f.name, version=o_version)
            o_package.store = o_store
            o_package.save()
    except:
        return return_message(cmd, error(GENERIC))

    return return_message(cmd, ok())

def upload_server_set(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    f = request.FILES["package"]
    filename = os.path.join(
        MIGASFREE_REPO_DIR,
        data['version'],
        "STORES",
        data['store'],
        data['packageset'],
        f.name
    )

    try:
        if Version.objects.filter(name=data['version']):
            o_version = Version.objects.get(name=data['version'])
        else:
            return return_message(cmd, error(VERSIONNOTFOUND))

        if Store.objects.filter(name=data['store'], version=o_version):
            o_store = Store.objects.get(name=data['store'], version=o_version)
        else:
            o_store = Store()
            o_store.name = data['store']
            o_store.version = o_version
            o_store.save()

        #we add the packageset and create the directory
        if Package.objects.filter(name=data['packageset'], version=o_version):
            o_package = Package.objects.get(
                name=data['packageset'],
                version=o_version
            )
        else:
            o_package = Package(name=data['packageset'], version=o_version)

        o_package.store = o_store
        o_package.save()
        o_package.create_dir()

        save_request_file(f, filename)

    except:
        return return_message(cmd, error(GENERIC))

    return return_message(cmd, ok())

def create_repositories_of_packageset(request, computer, data): #pylint: disable-msg=C0103
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    try:
        create_repositories_package(data['packageset'], data['version'])
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret

def save_request_file(requestfile, filename):
    """
    SAVE THE REQUEST FILE IN THE SERVER IN "FILENAME"
    """
    fp = open(filename, 'wb+')
    for chunk in requestfile.chunks():
        fp.write(chunk)
    fp.close()

    try:
        # https://docs.djangoproject.com/en/dev/topics/http/file-uploads/
        # Files with: Size > FILE_UPLOAD_MAX_MEMORY_SIZE  -> generate a file called something like /tmp/tmpzfp6I6.upload.
        # We remove it
        os.remove(requestfile.temporary_file_path)
    except:
        pass
