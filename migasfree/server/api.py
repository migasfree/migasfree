# -*- coding: utf-8 -*-

import os
import time
import inspect
from datetime import datetime
from datetime import timedelta

from django.db.models import Q
from django.contrib import auth

from . import jsontemplate

from migasfree.settings import (
    MIGASFREE_REPO_DIR,
    MIGASFREE_AUTOREGISTER,
    MIGASFREE_HW_PERIOD,
)

from migasfree.server.models import *
from migasfree.server.errmfs import *
from migasfree.server.functions import *
from migasfree.server.security import *
from migasfree.server.views import load_hw, create_physical_repository

import logging
logger = logging.getLogger('migasfree')


def add_notification_platform(platform, o_computer):
    o_notification = Notification()
    o_notification.notification = \
        "Platform [%s] registered by computer [%s]." % (
        platform,
        o_computer.__unicode__()
    )
    o_notification.date = time.strftime("%Y-%m-%d %H:%M:%S")
    o_notification.save()


def add_notification_version(version, pms, o_computer):
    o_notification = Notification()
    o_notification.notification = \
        "Version [%s] with P.M.S. [%s] registered by computer [%s]." \
        % (version, pms, o_computer.__unicode__())
    o_notification.date = time.strftime("%Y-%m-%d %H:%M:%S")
    o_notification.save()


def get_computer(name, uuid):
    logger.debug('name: %s, uuid: %s' % (name, uuid))
    if Computer.objects.filter(uuid=uuid):
        o_computer = Computer.objects.get(uuid=uuid)
        logger.debug('computer found by uuid')
    else:
        if Computer.objects.filter(name=name):
            o_computer = Computer.objects.get(name=name)
            logger.debug('computer found by name')
        else:
            o_computer = None
    return o_computer


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


def save_login(o_computer, o_user):
    login_date = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        o_login = Login.objects.get(
            computer=o_computer,
            user=o_user
        )
        o_login.date = login_date
        o_login.save()
    except:  # if Login not exists, we save it
        o_login = Login(
            computer=o_computer,
            user=o_user
        )
        o_login.date = login_date
        o_login.save()

    return  o_login


def upload_computer_hardware(request, name, uuid, o_computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        HwNode.objects.filter(computer=o_computer).delete()
        load_hw(o_computer, data[cmd], None, 1)
        o_computer.datehardware = time.strftime("%Y-%m-%d %H:%M:%S")
        o_computer.save()
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_software_base_diff(request, name, uuid, o_computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        o_computer.software = data[cmd]
        o_computer.save()
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_software_base(request, name, uuid, o_computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        o_version = o_computer.version
        o_version.base = data[cmd]
        o_version.save()
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_software_history(request, name, uuid, o_computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        o_computer.history_sw = "%s\n\n%s" % (o_computer.history_sw, data[cmd])
        o_computer.save()
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def get_computer_software(request, name, uuid, o_computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        ret = return_message(
            cmd,
            o_computer.version.base
        )
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_errors(request, name, uuid, o_computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        o_version = o_computer.version
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


def upload_computer_message(request, name, uuid, o_computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    date_now = time.strftime("%Y-%m-%d %H:%M:%S")

    if not o_computer:
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
                user_id=o_computer.last_login().user_id,
                date=date_now,
                version=o_computer.version
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


def get_properties(request, name, uuid, o_computer, data):
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
        for e in Property.objects.filter(active=True).filter(
            tag=False
        ).exclude(prefix="CID"):  # FIXME improve exclusion method
            properties.append({
                "language": LANGUAGES_CHOICES[e.language][1],
                "name": e.prefix,
                "code": e.code
            })

        ret = return_message(cmd, {"properties": properties})
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_info(request, name, uuid, o_computer, data):
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
                "hardware_capture": true|false,
                "devices":
                    {
                        "install": bashcode ,
                        "remove": bashcode
                    } #TODO move code to client
    """

    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    m = time.strftime("%Y-%m-%d %H:%M:%S")

    platform = data.get("upload_computer_info").get("computer").get(
        'platform',
        'unknown'
    )
    version = data.get("upload_computer_info").get("computer").get(
        'version',
        'unknown'
    )
    pms = data.get("upload_computer_info").get("computer").get(
        'pms',
        'apt-get'
    )

    notify_platform = False
    notify_version = False

    # Autoregister Platform
    if not Platform.objects.filter(name=platform):
        if not MIGASFREE_AUTOREGISTER:
            return return_message(cmd, error(CANNOTREGISTER))
        # if all ok we add the platform
        o_platform = Platform()
        o_platform.name = platform
        o_platform.save()

        notify_platform = True

    # Autoregister Version
    if not Version.objects.filter(name=version):
        if not MIGASFREE_AUTOREGISTER:
            return return_message(cmd, error(CANNOTREGISTER))
        # if all ok we add the version
        o_version = Version()
        o_version.name = version
        o_version.pms = Pms.objects.get(name=pms)
        o_version.platform = Platform.objects.get(name=platform)
        o_version.autoregister = MIGASFREE_AUTOREGISTER
        o_version.save()

        notify_version = True

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

        #registration of ip, version an Migration of computer
        o_computer = check_computer(
            o_computer,
            name,
            dic_computer.get("version"),
            dic_computer.get("ip", ""),
            uuid,
        )

        if notify_platform:
            add_notification_platform(platform, o_computer)

        if notify_version:
            add_notification_version(version, pms, o_computer)

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
        o_login = save_login(
            o_computer,
            User.objects.get(name=dic_computer["user"])
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

        # add Tags (not running on clients!!!)
        for tag in o_computer.tags.all().filter(property_att__active=True):
            lst_attributes.append(
                new_attribute(o_login, tag.property_att, tag.value)
            )

        # ADD ATTRIBUTE CID (not running on clients!!!)
        try:
            prp_cid = Property.objects.get(prefix="CID", active=True)
            if prp_cid:
                lst_attributes.append(
                    new_attribute(o_login, prp_cid, str(o_computer.id))
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

        repositories = select_repositories(o_version, lst_attributes)

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
        retdata["base"] = (o_version.computerbase == o_computer.__unicode__())

        #HARDWARE CAPTURE
        if o_computer.datehardware:
            hwcapture = (datetime.now() > (
                o_computer.datehardware + timedelta(days=MIGASFREE_HW_PERIOD))
            )
        else:
            hwcapture = True
        retdata["hardware_capture"] = hwcapture

        ret = return_message(cmd, retdata)
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_faults(request, name, uuid, o_computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    faults = data.get(cmd).get("faults")
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
def get_device(request, name, uuid, o_computer, data):
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


def get_assist_devices(request, name, uuid, o_computer, data):
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


def remove_device(request, name, uuid, o_computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    d = data[cmd]
    try:
        o_device = Device.objects.get(name=d["NUMBER"])
        try:
            o_device.computer_set.remove(o_computer)
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


def install_device(request, name, uuid, o_computer, data):
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

    o_device.computer_set.add(o_computer)
    o_device.save()
    list_computers = []
    for c in o_device.computer_set.all():
        list_computers.append(c.name)

    return return_message(cmd, {
        "NUMBER": o_device.name,
        "COMPUTERS": list_computers
    })


def register_computer(request, name, uuid, o_computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    user = auth.authenticate(
        username=data.get('username'),
        password=data.get('password')
    )

    platform = data.get('platform', 'unknown')
    version = data.get('version', 'unknown')
    pms = data.get('pms', 'apt-get')

    notify_platform = False
    notify_version = False

    # Autoregister Platform
    if not Platform.objects.filter(name=platform):
        if not MIGASFREE_AUTOREGISTER:
            if not user or not user.has_perm("server.can_save_platform"):
                return return_message(cmd, error(CANNOTREGISTER))
        # if all ok we add the platform
        o_platform = Platform()
        o_platform.name = platform
        o_platform.save()

        notify_platform = True

    # Autoregister Version
    if not Version.objects.filter(name=version):
        if not MIGASFREE_AUTOREGISTER:
            if not user or not user.has_perm("server.can_save_version"):
                return return_message(cmd, error(CANNOTREGISTER))
        # if all ok we add the version
        o_version = Version()
        o_version.name = version
        o_version.pms = Pms.objects.get(name=pms)
        o_version.platform = Platform.objects.get(name=platform)
        o_version.autoregister = MIGASFREE_AUTOREGISTER
        o_version.save()

        notify_version = True

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
        o_computer = check_computer(
            o_computer,
            name,
            data.get('version'),
            data.get('ip', ''),
            uuid
            )

        if notify_platform:
            add_notification_platform(platform, o_computer)

        if notify_version:
            add_notification_version(version, pms, o_computer)

        # 2.- returns keys to client
        return return_message(cmd, get_keys_to_client(data['version']))

    return return_message(cmd, error(USERHAVENOTPERMISSION))


def get_key_packager(request, name, uuid, o_computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    user = auth.authenticate(
        username=data['username'],
        password=data['password']
    )
    if not user.has_perm("server.can_save_package"):
        return return_message(cmd, error(CANNOTREGISTER))

    return return_message(cmd, get_keys_to_packager())


def upload_server_package(request, name, uuid, o_computer, data):
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


def upload_server_set(request, name, uuid, o_computer, data):
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


def set_computer_tags(request, name, uuid, o_computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    tags = data["set_computer_tags"]["tags"]
    select = data["set_computer_tags"]["select"]
    if select:
        retdata = ok()
        retdata["select"] = {}
        element = []
        for tag in o_computer.tags.all():
            element.append("%s-%s" % (tag.property_att.prefix, tag.value))
        retdata["select"]["tags"] = element

        retdata["select"]["availables"] = {}
        for prp in Property.objects.filter(tag=True).filter(active=True):
            retdata["select"]["availables"][prp.name] = []
            for tag in Attribute.objects.filter(property_att=prp):
                retdata["select"]["availables"][prp.name].append("%s-%s" %
                    (prp.prefix, tag.value))

        return return_message(cmd, retdata)


    all_id = Attribute.objects.get(
        property_att__prefix="ALL",
        value="ALL SYSTEMS"
        ).id
    try:
        lst_tags_obj = []
        lst_tags_id = []
        for tag in tags:
            ltag = tag.split("-", 1)
            o_attribute = Attribute.objects.get(
                    property_att__prefix=ltag[0],
                    value=ltag[1]
                    )
            lst_tags_obj.append(o_attribute)
            lst_tags_id.append(o_attribute.id)
        lst_tags_id.append(all_id)

        lst_computer_id = []
        for tag in o_computer.tags.all():
            lst_computer_id.append(tag.id)
        lst_computer_id.append(all_id)

        retdata = ok()
        (old_tags_id, new_tags_id) = old_new_elements(
            lst_computer_id,
            lst_tags_id
            )
        com_tags_id = list_common(lst_computer_id, lst_tags_id)

        lst_pkg_remove = []
        lst_pkg_install = []
        lst_pkg_preinstall = []

        # Repositories old
        repositories = select_repositories(o_computer.version, old_tags_id)
        for r in repositories:
            # INVERSE !!!!
            pkgs = "%s %s %s" % (
                r.toinstall,
                r.defaultinclude,
                r.defaultpreinclude
                )
            for p in pkgs.replace("\r", " ").replace("\n", " ").split(" "):
                if p != "" and p != 'None':
                    lst_pkg_remove.append(p)
            pkgs = "%s %s" % (
                r.toremove,
                r.defaultexclude
                )
            for p in pkgs.replace("\r", " ").replace("\n", " ").split(" "):
                if p != "" and p != 'None':
                    lst_pkg_install.append(p)

        # Repositories new
        repositories = select_repositories(o_computer.version, new_tags_id + com_tags_id)
        for r in repositories:
            pkgs = "%s %s" % (
                r.toremove,
                r.defaultexclude
                )
            for p in pkgs.replace("\r", " ").replace("\n", " ").split(" "):
                if p != "" and p != 'None':
                    lst_pkg_remove.append(p)
            pkgs = "%s %s" % (
                r.toinstall,
                r.defaultinclude
                )
            for p in pkgs.replace("\r", " ").replace("\n", " ").split(" "):
                if p != "" and p != 'None':
                    lst_pkg_install.append(p)
            pkgs = "%s" % (
                r.defaultpreinclude,
                )
            for p in pkgs.replace("\r", " ").replace("\n", " ").split(" "):
                if p != "" and p != 'None':
                    lst_pkg_preinstall.append(p)

        retdata["packages"] = {
            "preinstall": lst_pkg_preinstall,
            "install": lst_pkg_install,
            "remove": lst_pkg_remove,
            }

        # Modify computer tags
        o_computer.tags = lst_tags_obj

        ret = return_message(cmd, retdata)
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def add_migration(o_computer, o_version):
    o_migration = Migration()
    o_migration.computer = o_computer
    o_migration.version = o_version
    o_migration.date = time.strftime("%Y-%m-%d %H:%M:%S")
    o_migration.save()


def check_computer(o_computer, name, version, ip, uuid):
    #registration of ip, version, uuid and Migration of computer
    o_version = Version.objects.get(name=version)

    if not o_computer:
        o_computer = Computer()
        o_computer.name = name
        o_computer.dateinput = time.strftime("%Y-%m-%d")
        o_computer.version = o_version
        o_computer.uuid = uuid
        o_computer.save()
        add_migration(o_computer, o_version)

    # Check Migration
    if o_computer.version != o_version:
        add_migration(o_computer, o_version)

    o_computer.name = name
    o_computer.version = o_version
    o_computer.ip = ip
    o_computer.uuid = uuid
    o_computer.save()
    return o_computer


def create_repositories_package(packagename, versionname):
    o_version = Version.objects.get(name=versionname)
    try:
        package = Package.objects.get(name=packagename, version=o_version)
        qset = Repository.objects.filter(packages__id=package.id)
        for repo in qset:
            create_physical_repository(repo)
    except:
        pass


def create_repositories_of_packageset(request, name, uuid, o_computer, data):
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


def select_repositories(o_version, lst_attributes):
    """
    Return the repositories availables for a version and attributes list
    """
    dic_repos = {}

    # 1.- Add to "dic_repos" all repositories by attribute
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

    # 2.- Add to "dic_repos" all repositories by schedule
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

    # 3.- Attributtes Excluded
    repositories = Repository.objects.filter(
        Q(id__in=dic_repos.values())
    )

    repositories = repositories.filter(~Q(excludes__id__in=lst_attributes))

    return repositories
