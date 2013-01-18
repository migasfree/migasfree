# -*- coding: utf-8 -*-

import os
import time
import inspect
from datetime import datetime
from datetime import timedelta


from django.db.models import Q
from django.contrib import auth

from . import jsontemplate

from migasfree.settings import MIGASFREE_REPO_DIR
from migasfree.settings import MIGASFREE_AUTOREGISTER
from migasfree.settings import MIGASFREE_HW_PERIOD

from migasfree.server.models import *
from migasfree.server.errmfs import *
from migasfree.server.functions import *
from migasfree.server.security import *
from migasfree.server.views import load_hw, create_repositories


def new_attribute(o_login, o_property, par):
    """
    Adds an attribute to the system
        par is a "value~name" string or only "value"

    Returns id of new attribute
    """
    reg = par.split("~")
    value_att = reg[0].strip()
    if len(reg) > 1:
        description_att = reg[1]
    else:
        description_att = ""

    # Add the attribute
    if value_att != "":
        try:
            o_attribute = Attribute.objects.get(
                value=value_att,
                property_att__id=o_property.id
            )
        except:  # if not exist the attribute, we add it
            if o_property.auto is True:
                o_attribute = Attribute()
                o_attribute.property_att = o_property
                o_attribute.value = value_att
                o_attribute.description = description_att
                o_attribute.save()

    # Add the attribute to Login
    o_login.attributes.add(o_attribute)

    return o_attribute.id


def save_login(pc, user):
    login_date = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        o_login = Login.objects.get(
            computer=Computer.objects.get(name=pc),
            user=User.objects.get(name=user)
        )
        o_login.date = login_date
        o_login.save()
    except:  # if Login not exists, we save it
        o_login = Login(
            computer=Computer.objects.get(name=pc),
            user=User.objects.get(name=user)
        )
        o_login.date = login_date
        o_login.save()

    return  # ???


def upload_computer_hardware(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        o_computer = Computer.objects.get(name=computer)
        HwNode.objects.filter(computer=o_computer).delete()
        load_hw(o_computer, data[cmd], None, 1)
        o_computer.datehardware = time.strftime("%Y-%m-%d %H:%M:%S")
        o_computer.save()
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_software_base_diff(request, computer, data):
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
        o_version = Version.objects.get(
            name=Computer.objects.get(name=computer).version
        )
        o_version.base = data[cmd]
        o_version.save()
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_software_history(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        o_computer = Computer.objects.get(name=computer)
        o_computer.history_sw = str(o_computer.history_sw) + "\n\n" + data[cmd]
        o_computer.save()
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def get_computer_software(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        o_computer = Computer.objects.get(name=computer)
        ret = return_message(
            cmd,
            Version.objects.get(name=o_computer.version).base
        )
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_errors(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        o_computer = Computer.objects.get(name=computer)
        o_version = Version.objects.get(id=o_computer.version_id)
        o_error = Error()
        o_error.computer = o_computer
        o_error.date = time.strftime("%Y-%m-%d %H:%M:%S")
        o_error.error = data[cmd]
        o_error.version = o_version
        o_error.save()
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_message(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    date_now = time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        o_computer = Computer.objects.get(name=computer)
    except:
        return return_message(cmd, error(COMPUTERNOTFOUND))

    try:
        o_message = Message.objects.get(computer=o_computer)
        if data[cmd] == "":
            o_message.delete()
    except:
        o_message = Message(computer=o_computer)

    try:
        if data[cmd] == "":
            Update(
                computer=o_computer,
                date=date_now,
                version=Version.objects.get(name=o_computer.version)
            ).save()
        else:
            o_message.text = data[cmd]
            o_message.date = date_now
            o_message.save()
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def return_message(cmd, data):
    return {'%s.return' % cmd: data}


def get_properties(request, computer, data):
    """
    First call of client requesting to server what he must do.
    The server responds with a string json with structure:

        OUTPUT:
        ======
            {
                "properties":
                    [
                        {
                            "prefix": "PREFIX",
                            "function": "CODE" ,
                            "language": "LANGUAGE"
                        },
                        ...
                    ],
            }

    The client will eval the "functions" in PROPERTIES and FAULTS and
    will upload it to server in a file called request.json
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

        ret = return_message(cmd, {"properties": properties})

    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_info(request, computer, data):
    """
    Process the file request.json and return a string json with the faultsdef,
    repositories, packages and devices
        INPUT:
        =====
        A file "request.json" with the result of evaluate the request obtained
        by "get_regest"

            {
              "computer":
                  {
                      "hostname": HOSTNAME,
                      "ip": IP,
                      "platform": PLATFORM,
                      "version": VERSION,
                      "user": USER,
                      "user_fullname": USER_FULLNAME
                  },
              "attributes":[{"name":VALUE},...]
            }

        OUTPUT:
        ======
        After of process this file the server respond to client with
        a string json with:

            {
                "faultsdef": [
                    {
                        "name":"NAME",
                        "function":"CODE",
                        "language": "LANGUAGE"
                    },
                    ...] ,
                "repositories" : [ {"name": "REPONAME" }, ...] ,
                "packages":
                    {
                        "install": ["pck1","pck2","pck3",...],
                        "remove": ["pck1","pck2","pck3",...]
                    } ,
                "base": true|false,
                "hardware": true|false,
                "devices":
                    {
                        "install": bashcode ,
                        "remove": bashcode
                    } #TODO move code to client
    """

    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    t = time.strftime("%Y-%m-%d")
    m = time.strftime("%Y-%m-%d %H:%M:%S")

    platform = data.get("upload_computer_info").get("computer").get('platform', 'unknown')
    version = data.get("upload_computer_info").get("computer").get('version', 'unknown')

    # Autoregister Platform
    if not Platform.objects.filter(name=platform):
        if not MIGASFREE_AUTOREGISTER:
                return return_message(cmd, error(CANNOTREGISTER))
        # if all ok we add the platform
        o_platform = Platform()
        o_platform.name = platform
        o_platform.save()

        o_messageserver = MessageServer()
        o_messageserver.text = "PLATFORM [%s] REGISTERED BY COMPUTER [%s]." % (platform, computer)
        o_messageserver.date = time.strftime("%Y-%m-%d %H:%M:%S")
        o_messageserver.save()

    # Autoregister Version
    if not Version.objects.filter(name=version):
        if not MIGASFREE_AUTOREGISTER:
                return return_message(cmd, error(CANNOTREGISTER))
        # if all ok we add the version
        o_version = Version()
        o_version.name = version
        o_version.pms = Pms.objects.get(id=1)  # default
        o_version.platform = Platform.objects.get(name=platform)
        o_version.autoregister = MIGASFREE_AUTOREGISTER
        o_version.save()

        o_messageserver = MessageServer()
        o_messageserver.text = "VERSION [%s] REGISTERED BY COMPUTER[%s]. Please check the PMS." % (version, computer)
        o_messageserver.date = time.strftime("%Y-%m-%d %H:%M:%S")
        o_messageserver.save()


    lst_attributes = []  # List of attributes of computer

    ret = ""

    try:
        dic_computer = data.get("upload_computer_info").get("computer")
        properties = data.get("upload_computer_info").get("attributes")

        # 1.- PROCESS COMPUTER
        if dic_computer["hostname"] == "desktop":
            str_error = trans(
                'desktop is not valid name for this computer: IP=%(ip)s'
            ) % {'ip': dic_computer["ip"]}
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
            o_computer.version = Version.objects.get(
                name=dic_computer["version"]
            )
            o_computer.save()
        except:  # if not exists the computer, we add it
            o_computer = Computer(name=dic_computer["hostname"])
            o_computer.dateinput = t
            o_computer.ip = dic_computer["ip"]
            o_computer.version = Version.objects.get(
                name=dic_computer["version"]
            )
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
        o_login = Login.objects.get(
            computer=Computer.objects.get(name=dic_computer["hostname"]),
            user=User.objects.get(name=dic_computer["user"])
        )
        o_login.attributes.clear()

        # Get version
        version = dic_computer["version"]

        o_version = Version.objects.get(name=version)

        # Get the Package Management System
        #o_pms = Pms.objects.get(id=o_version.pms.id)

        # 2.- PROCESS PROPERTIES
        for e in properties:
            o_property = Property.objects.get(prefix=e)
            value = properties.get(e)
            try:

                # NORMAL
                if o_property.kind == "N":
                    lst_attributes.append(
                        new_attribute(o_login, o_property, value)
                    )

                # LIST
                if o_property.kind == "-":
                    mylist = value.split(",")
                    for element in mylist:
                        lst_attributes.append(
                            new_attribute(o_login, o_property, element)
                        )

                # ADDS RIGHT
                if o_property.kind == "R":
                    lista = value.split(".")
                    c = value
                    l = 0
                    for x in lista:
                        lst_attributes.append(
                            new_attribute(o_login, o_property, c[l:])
                        )
                        l += len(x) + 1

                # ADDS LEFT
                if o_property.kind == "L":
                    lista = value.split(".")
                    c = value
                    l = 0
                    for x in lista:
                        l += len(x) + 1
                        lst_attributes.append(
                            new_attribute(o_login, o_property, c[0:l - 1])
                        )

            except:
                pass

        # 3 FaultsDef
        lst_faultsdef = []
        faultsdef = FaultDef.objects.filter(
            Q(attributes__id__in=lst_attributes)
        )
        faultsdef = faultsdef.filter(Q(active=True))
        for d in faultsdef:
            lst_faultsdef.append({
                "language": LANGUAGES_CHOICES[d.language][1],
                "name": d.name,
                "code": d.code
            })

        dic_repos = {}

        repositories = Repository.objects.filter(
            Q(attributes__id__in=lst_attributes),
            Q(version__id=o_version.id)
        )
        repositories = repositories.filter(
            Q(version__id=o_version.id),
            Q(active=True)
        )

        for r in repositories:
            dic_repos[r.name] = r.id

        repositories = Repository.objects.filter(
            Q(schedule__scheduledelay__attributes__id__in=lst_attributes),
            Q(active=True)
        )
        repositories = repositories.filter(
            Q(version__id=o_version.id),
            Q(active=True)
        )
        repositories = repositories.extra(
            select={'delay': "server_scheduledelay.delay"}
        )

        for r in repositories:
            if horizon(r.date, r.delay) <= datetime.now().date():
                dic_repos[r.name] = r.id

        repositories = Repository.objects.filter(
            Q(id__in=dic_repos.values())
        )

        #FILTER EXCLUDED ATTRIBUTES
        repositories = repositories.filter(~Q(excludes__id__in=lst_attributes))

        #4.- CREATE JSON
        lst_repos = []
        lst_pkg_remove = []
        lst_pkg_install = []

        for r in repositories:
            lst_repos.append({"name": r.name})
            for p in r.toremove.replace("\n", " ").split(" "):
                if p != "":
                    lst_pkg_remove.append(p)
            for p in r.toinstall.replace("\n", " ").split(" "):
                if p != "":
                    lst_pkg_install.append(p)

        #DEVICES
        lst_dev_remove = []
        lst_dev_install = []
        chk_devices = Mmcheck(o_computer.devices, o_computer.devices_copy)
        if chk_devices.changed() is True \
        or o_computer.devices_modified is True:
            #remove the devices
            lst_diff = list_difference(
                s2l(o_computer.devices_copy),
                s2l(chk_devices.mms())
            )
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
        retdata["packages"] = {
            "remove": lst_pkg_remove,
            "install": lst_pkg_install
        }
        retdata["devices"] = {
            "remove": lst_dev_remove,
            "install": lst_dev_install
        }
        retdata["base"] = (o_version.computerbase == o_computer.name)

        #HARDWARE CAPTURE
        if o_computer.datehardware:
            hwcapture = ( datetime.now() > (o_computer.datehardware + timedelta(days=MIGASFREE_HW_PERIOD)) )
        else:
            hwcapture = True
        retdata["hardwarecapture"] = hwcapture

        ret = return_message(cmd, retdata)
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_faults(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    faults = data.get(cmd).get("faults")
    o_computer = Computer.objects.get(name=computer)
    o_version = Version.objects.get(id=o_computer.version_id)

    try:
        # PROCESS FAULTS
        for e in faults:
            o_faultdef = FaultDef.objects.get(name=e)
            try:
                msg = faults.get(e)
                if msg != "":
                    # we add the fault
                    o_fault = Fault()
                    o_fault.computer = o_computer
                    o_fault.date = time.strftime("%Y-%m-%d %H:%M:%S")
                    o_fault.text = msg
                    o_fault.faultdef = o_faultdef
                    o_fault.version = o_version
                    o_fault.save()
            except:
                pass

        ret = return_message(cmd, {})
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


#DEVICES
def get_device(request, computer, data):
    """
    Returns DeviceModel data for lpadmin
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
            for dev_model_man in DeviceModel.objects.filter(
                devicetype__id=dev_type.id
            ).distinct():
                models = {}

                for dev_model in DeviceModel.objects.filter(
                    manufacturer__id=dev_model_man.manufacturer.id
                ):
                    ports = {}

                    for dev_port in dev_model.connections.all():
                        parameters = {}

                        for token_type, token in jsontemplate._Tokenize(
                            dev_port.uri,
                            '{',
                            '}'
                        ):
                            if token_type == 1:
                                parameters[token] = {"default": ""}

                        parameters["LOCATION"] = {"default": ""}
                        parameters["INFORMATION"] = {"default": ""}
                        parameters["ALIAS"] = {"default": ""}

                        ports[dev_port.name] = {
                            "type": "inputbox",
                            "name": "PARAMETER",
                            "value": parameters
                        }
                    models[dev_model.name] = {
                        "type": "menu",
                        "name": "PORT",
                        "value": ports
                    }
                manufacters[dev_model_man.manufacturer.name] = {
                    "type": "menu",
                    "name": "MODEL",
                    "value": models
                }
            types[dev_type.name] = {
                "type": "menu",
                "name": "MANUFACTURER",
                "value": manufacters
            }
        ret = return_message(cmd, {
            "type": "menu",
            "name": "TYPE",
            "value": types
        })
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
            return return_message(cmd, {
                "NUMBER": o_device.name,
                "COMPUTERS": list_computers
            })
        except:
            return return_message(cmd, error(GENERIC))
    except:  # if not exists device
        return return_message(cmd, error(DEVICENOTFOUND))


def install_device(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    d = data[cmd]

    try:
        o_device = Device.objects.get(name=d["NUMBER"])
    except:  # if not exists device
        try:
            o_device = Device()
            o_device.name = d["NUMBER"]
            o_device.alias = d["ALIAS"]
            o_devicemodel = DeviceModel.objects.get(name=d["MODEL"])
            o_device.model = o_devicemodel

            o_devicetype = DeviceType.objects.get(name=d["TYPE"])
            o_deviceconnection = DeviceConnection.objects.get(
                name=d["PORT"],
                devicetype=o_devicetype
            )
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

    return return_message(cmd, {
        "NUMBER": o_device.name,
        "COMPUTERS": list_computers
    })


def register_computer(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    user = auth.authenticate(
        username=data.get('username'),
        password=data.get('password')
    )

    platform = data.get('platform', 'unknown')
    version = data.get('version', 'unknown')

    # Autoregister Platform
    if not Platform.objects.filter(name=platform):
        if not MIGASFREE_AUTOREGISTER:
            if not user or not user.has_perm("server.can_save_platform"):
                return return_message(cmd, error(CANNOTREGISTER))
        # if all ok we add the platform
        o_platform = Platform()
        o_platform.name = platform
        o_platform.save()

        o_messageserver = MessageServer()
        o_messageserver.text = "PLATFORM [%s] REGISTERED BY COMPUTER [%s]." % (platform, computer)
        o_messageserver.date = time.strftime("%Y-%m-%d %H:%M:%S")
        o_messageserver.save()

    # Autoregister Version
    if not Version.objects.filter(name=version):
        if not MIGASFREE_AUTOREGISTER:
            if not user or not user.has_perm("server.can_save_version"):
                return return_message(cmd, error(CANNOTREGISTER))
        # if all ok we add the version
        o_version = Version()
        o_version.name = version
        o_version.pms = Pms.objects.get(id=1)  # default
        o_version.platform = Platform.objects.get(name=platform)
        o_version.autoregister = MIGASFREE_AUTOREGISTER
        o_version.save()

        o_messageserver = MessageServer()
        o_messageserver.text = "VERSION [%s] REGISTERED BY COMPUTER[%s]. Please check the PMS." % (version, computer)
        o_messageserver.date = time.strftime("%Y-%m-%d %H:%M:%S")
        o_messageserver.save()

    # REGISTER COMPUTER
    # Check Version
    if Version.objects.filter(name=data['version']):
        o_version = Version.objects.get(name=data['version'])
        # if not autoregister, check that the user can save computer
        if not o_version.autoregister:
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
        return return_message(cmd, get_keys_to_client(data['version']))

    return return_message(cmd, error(USERHAVENOTPERMISSION))


def get_key_packager(request, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    user = auth.authenticate(
        username=data['username'],
        password=data['password']
    )
    if not user.has_perm("server.can_save_package"):
        return return_message(cmd, error(CANNOTREGISTER))

    return return_message(cmd, get_keys_to_packager())


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

        # if exists path move it
        if ("path" in data) and (data["path"] != ""):
            dst = os.path.join(
                MIGASFREE_REPO_DIR,
                data['version'],
                "STORES",
                data['store'],
                data['packageset'],
                data['path'],
                f.name)
            try:
                os.makedirs(os.path.dirname(dst))
            except:
                pass
            os.rename(filename, dst)

    except:
        return return_message(cmd, error(GENERIC))

    return return_message(cmd, ok())


def create_repositories_package(packagename, versionname):
    o_version = Version.objects.get(name=versionname)
    try:
        package = Package.objects.get(name=packagename, version=o_version)
        qset = Repository.objects.filter(packages__id=package.id)
        for r in qset:
            for p in r.createpackages.all():
                r.createpackages.remove(p.id)
            r.save()
        create_repositories(package.version.id)
    except:
        pass


def create_repositories_of_packageset(request, computer, data):
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
        # Files with: Size > FILE_UPLOAD_MAX_MEMORY_SIZE  -> generate a file
        # called something like /tmp/tmpzfp6I6.upload.
        # We remove it
        os.remove(requestfile.temporary_file_path)
    except:
        pass
