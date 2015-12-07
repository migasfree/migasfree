# -*- coding: utf-8 -*-

import os
import time
import inspect
from datetime import datetime, timedelta

from django.db.models import Q
from django.contrib import auth
from django.conf import settings
from django.utils.translation import ugettext

from .models import *
from .errmfs import *
from .functions import *
from .security import *
from .views import load_hw
from .tasks import create_physical_repository

import logging
logger = logging.getLogger('migasfree')


def add_notification_platform(platform, computer):
    Notification.objects.create(
        "Platform [%s] registered by computer [%s]." % (
            platform,
            computer.__unicode__()
        )
    )


def add_notification_version(version, pms, computer):
    Notification.objects.create(
        "Version [%s] with P.M.S. [%s] registered by computer [%s]." % (
            version,
            pms,
            computer.__unicode__()
        )
    )


def get_computer(name, uuid):
    '''
    Returns a computer object (or None if not found)
    '''
    logger.debug('name: %s, uuid: %s' % (name, uuid))
    computer = None

    try:
        computer = Computer.objects.get(uuid=uuid)
        logger.debug('computer found by uuid')

        return computer
    except Computer.DoesNotExist:
        pass

    try:  # search with endian format changed
        computer = Computer.objects.get(uuid=uuid_change_format(uuid))
        logger.debug('computer found by uuid (endian format changed)')

        return computer
    except Computer.DoesNotExist:
        pass

    # DEPRECATED This Block. Only for compatibilty with client <= 2
    message = 'computer found by name. compatibility mode'
    if len(uuid.split("-")) == 5:  # search for uuid (client >= 3)
        try:
            computer = Computer.objects.get(uuid=name)
            logger.debug(message)

            return computer
        except Computer.DoesNotExist:
            pass
    else:
        try:
            # search for name (client <= 2)
            computer = Computer.objects.get(name=name, uuid=name)
            logger.debug(message)

            return computer
        except Computer.DoesNotExist:
            try:
                computer = Computer.objects.get(name=name)
                logger.debug(message)

                return computer
            except Computer.DoesNotExist, Computer.MultipleObjectsReturned:
                pass

    if computer is None:
        logger.debug('computer not found!!!')

    return computer


def upload_computer_hardware(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        HwNode.objects.filter(computer=computer).delete()
        load_hw(computer, data[cmd], None, 1)
        computer.update_last_hardware_capture()
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_software_base_diff(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        computer.update_software_inventory(data[cmd])
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_software_base(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        version = Version.objects.get(pk=computer.version_id)
        version.update_base(data[cmd])

        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_software_history(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        computer.update_software_history(data[cmd])
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def get_computer_software(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        ret = return_message(
            cmd,
            computer.version.base
        )
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_errors(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        Error.objects.create(computer, computer.version, data[cmd])

        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_message(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    if not computer:
        return return_message(cmd, error(COMPUTER_NOT_FOUND))

    try:
        _message = Message.objects.get(computer=computer)
        if data[cmd] == "":
            _message.delete()
    except:
        _message = Message(computer=computer)

    try:
        if data[cmd] == "":
            Update.objects.create(computer)
        else:
            _message.update_message(data[cmd])
        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def return_message(cmd, data):
    return {'%s.return' % cmd: data}


def get_properties(request, name, uuid, computer, data):
    """
    First call of client requesting to server what he must do.
    The server responds with a string json with structure:

        OUTPUT:
        ======
            {
                "properties":
                    [
                        {
                            "name": "PREFIX",
                            "code": "CODE" ,
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
        for p in Property.enabled_client_properties():
            properties.append({
                "language": LANGUAGES_CHOICES[p['language']][1],
                "name": p['prefix'],
                "code": p['code']
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
        if not settings.MIGASFREE_AUTOREGISTER:
            return return_message(cmd, error(CAN_NOT_REGISTER_COMPUTER))

        # if all ok we add the platform
        o_platform = Platform.objects.create(platform)

        notify_platform = True

    # Autoregister Version
    if not Version.objects.filter(name=version):
        if not settings.MIGASFREE_AUTOREGISTER:
            return return_message(cmd, error(CAN_NOT_REGISTER_COMPUTER))

        # if all ok we add the version
        o_version = Version.objects.create(
            version,
            Pms.objects.get(name=pms),
            Platform.objects.get(name=platform),
            settings.MIGASFREE_AUTOREGISTER
        )

        notify_version = True

    lst_attributes = []  # List of attributes of computer

    ret = ""

    try:
        dic_computer = data.get("upload_computer_info").get("computer")
        properties = data.get("upload_computer_info").get("attributes")

        # 1.- PROCESS COMPUTER
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
        o_user, _ = User.objects.get_or_create(
            name=dic_computer["user"],
            fullname=dic_computer.get("user_fullname", "")
        )

        # Save Login
        o_login, _ = Login.objects.get_or_create(
            computer=o_computer,
            user=User.objects.get(name=dic_computer["user"])
        )
        o_login.attributes.clear()

        # Get version
        version = dic_computer.get("version")

        o_version = Version.objects.get(name=version)

        # 2.- PROCESS PROPERTIES
        for e in properties:
            o_property = Property.objects.get(prefix=e)
            value = properties.get(e)
            for att in Attribute.process_kind_property(o_property, value):
                o_login.attributes.add(att)
                lst_attributes.append(att)

        # ADD Tags (not running on clients!!!)
        for tag in o_computer.tags.all().filter(property_att__active=True):
            for att in Attribute.process_kind_property(
                tag.property_att,
                tag.value
            ):
                o_login.attributes.add(att)
                lst_attributes.append(att)

        # ADD ATTRIBUTE CID (not running on clients!!!)
        try:
            prp_cid = Property.objects.get(prefix="CID", active=True)
            if prp_cid:
                cid_description = o_computer.get_cid_description()
                cid = Attribute.objects.create(
                    prp_cid,
                    "%s~%s" % (str(o_computer.id), cid_description)
                )
                o_login.attributes.add(cid)
                lst_attributes.append(cid.id)

                cid.update_description(cid_description)
        except:
            pass

        # ADD AttributeSets
        lst_set = AttributeSet.process(lst_attributes)
        if lst_set:
            lst_attributes.extend(lst_set)
            o_login.attributes.add(lst_set)

        # 3 FaultsDef
        lst_faultsdef = []
        for d in FaultDef.enabled_for_attributes(lst_attributes):
            lst_faultsdef.append({
                "language": LANGUAGES_CHOICES[d.language][1],
                "name": d.name,
                "code": d.code
            })

        repositories = Repository.available_repos(o_computer, lst_attributes)

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
        chk_devices = Mmcheck(
            o_computer.devices_logical,
            o_computer.devices_copy
        )
        logger.debug('devices_logical %s' % vl2s(o_computer.devices_logical))
        logger.debug('devices_copy %s' % o_computer.devices_copy)
        if chk_devices.changed():
            # remove devices
            lst_diff = list_difference(
                s2l(o_computer.devices_copy),
                s2l(chk_devices.mms())
            )
            logger.debug('list diff: %s' % lst_diff)
            for item_id in lst_diff:
                try:
                    dev_logical = DeviceLogical.objects.get(id=item_id)
                    lst_dev_remove.append({
                        dev_logical.device.connection.devicetype.name: item_id
                    })
                except:
                    # maybe device_logical has been deleted
                    # FIXME harcoded values
                    lst_dev_remove.append({'PRINTER': item_id})

            # install devices
            lst_diff = list_difference(
                s2l(chk_devices.mms()),
                s2l(o_computer.devices_copy)
            )
            for item_id in lst_diff:
                try:
                    device_logical = DeviceLogical.objects.get(id=item_id)
                    lst_dev_install.append(
                        device_logical.datadict(o_computer.version)
                    )
                except:
                    pass

        logger.debug('install devices: %s' % lst_dev_install)
        logger.debug('remove devices: %s' % lst_dev_remove)

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
        hwcapture = True
        if o_computer.datehardware:
            hwcapture = (datetime.now() > (
                o_computer.datehardware + timedelta(
                    days=settings.MIGASFREE_HW_PERIOD
                ))
            )

        retdata["hardware_capture"] = hwcapture

        ret = return_message(cmd, retdata)
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


def upload_computer_faults(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    faults = data.get(cmd).get("faults")
    _version = Version.objects.get(id=computer.version_id)

    try:
        # PROCESS FAULTS
        for f in faults:
            try:
                msg = faults.get(f)
                if msg != "":
                    Fault.objects.create(
                        computer,
                        _version,
                        FaultDef.objects.get(name=f),
                        msg
                    )
            except:
                pass

        ret = return_message(cmd, {})
    except:
        ret = return_message(cmd, error(GENERIC))

    return ret


#DEVICES CHANGES
def upload_devices_changes(request, name, uuid, computer, data):
    logger.debug('upload_devices_changes data: %s' % data)
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        for devicelogical_id in data.get(cmd).get("installed", []):
            computer.append_device_copy(devicelogical_id)

        for devicelogical_id in data.get(cmd).get("removed", []):
            computer.remove_device_copy(devicelogical_id)

        ret = return_message(cmd, ok())
    except:
        ret = return_message(cmd, error(GENERIC))

    logger.debug('upload_devices_changes ret: %s' % ret)
    return ret


def register_computer(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    user = auth.authenticate(
        username=data.get('username'),
        password=data.get('password')
    )

    platform_name = data.get('platform', 'unknown')
    version_name = data.get('version', 'unknown')
    pms_name = data.get('pms', 'apt-get')

    notify_platform = False
    notify_version = False

    # Autoregister Platform
    if not Platform.objects.filter(name=platform_name):
        if not settings.MIGASFREE_AUTOREGISTER:
            if not user or not user.has_perm("server.can_save_platform"):
                return return_message(cmd, error(CAN_NOT_REGISTER_COMPUTER))

        # if all ok we add the platform
        platform = Platform.objects.create(platform_name)

        notify_platform = True

    # Autoregister Version
    if not Version.objects.filter(name=version_name):
        if not settings.MIGASFREE_AUTOREGISTER:
            if not user or not user.has_perm("server.can_save_version"):
                return return_message(cmd, error(CAN_NOT_REGISTER_COMPUTER))

        # if all ok we add the version
        version = Version.objects.create(
            version_name,
            Pms.objects.get(name=pms_name),
            Platform.objects.get(name=platform_name),
            settings.MIGASFREE_AUTOREGISTER
        )

        notify_version = True

    # REGISTER COMPUTER
    # Check Version
    try:
        version = Version.objects.get(name=version_name)
        # if not autoregister, check that the user can save computer
        if not version.autoregister:
            if not user or not user.has_perm("server.can_save_computer"):
                return return_message(cmd, error(CAN_NOT_REGISTER_COMPUTER))

        # ALL IS OK
        # 1.- Add Computer
        o_computer = check_computer(
            computer,
            name,
            version_name,
            data.get('ip', ''),
            uuid
        )

        if notify_platform:
            add_notification_platform(platform_name, o_computer)

        if notify_version:
            add_notification_version(version_name, pms_name, o_computer)

        # 2.- returns keys to client
        return return_message(cmd, get_keys_to_client(version_name))
    except:
        return return_message(cmd, error(USER_DOES_NOT_HAVE_PERMISSION))


def get_key_packager(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    user = auth.authenticate(
        username=data['username'],
        password=data['password']
    )
    if not user.has_perm("server.can_save_package"):
        return return_message(cmd, error(CAN_NOT_REGISTER_COMPUTER))

    return return_message(cmd, get_keys_to_packager())


def upload_server_package(request, name, uuid, o_computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    f = request.FILES["package"]
    filename = os.path.join(
        settings.MIGASFREE_REPO_DIR,
        data['version'],
        'STORES',
        data['store'],
        f.name
    )

    try:
        o_version = Version.objects.get(name=data['version'])
    except:
        return return_message(cmd, error(VERSION_NOT_FOUND))

    o_store, _ = Store.objects.get_or_create(
        name=data['store'], version=o_version
    )

    save_request_file(f, filename)

    # we add the package
    if not data['source']:
        o_package, _ = Package.objects.get_or_create(
            name=f.name,
            version=o_version,
            store=o_store
        )

    return return_message(cmd, ok())


def upload_server_set(request, name, uuid, o_computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    f = request.FILES["package"]
    filename = os.path.join(
        settings.MIGASFREE_REPO_DIR,
        data['version'],
        "STORES",
        data['store'],
        data['packageset'],
        f.name
    )

    try:
        o_version = Version.objects.get(name=data['version'])
    except:
        return return_message(cmd, error(VERSION_NOT_FOUND))

    o_store, _ = Store.objects.get_or_create(
        name=data['store'], version=o_version
    )

    # we add the packageset and create the directory
    o_package, _ = Package.objects.get_or_create(
        name=data['packageset'],
        version=o_version,
        store=o_store
    )
    o_package.create_dir()

    save_request_file(f, filename)

    # if exists path move it
    if ("path" in data) and (data["path"] != ""):
        dst = os.path.join(
            settings.MIGASFREE_REPO_DIR,
            data['version'],
            "STORES",
            data['store'],
            data['packageset'],
            data['path'],
            f.name
        )
        try:
            os.makedirs(os.path.dirname(dst))
        except:
            pass
        os.rename(filename, dst)

    return return_message(cmd, ok())


def get_computer_tags(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    retdata = ok()
    element = []
    for tag in computer.tags.all():
        element.append("%s-%s" % (tag.property_att.prefix, tag.value))
    retdata["selected"] = element

    retdata["available"] = {}
    for rps in Repository.objects.all().filter(
        version=computer.version
    ).filter(active=True):
        for tag in rps.attributes.all().filter(
            property_att__tag=True
        ).filter(property_att__active=True):
            if not tag.property_att.name in retdata["available"]:
                retdata["available"][tag.property_att.name] = []

            value = "%s-%s" % (tag.property_att.prefix, tag.value)
            if not value in retdata["available"][tag.property_att.name]:
                retdata["available"][tag.property_att.name].append(value)

    return return_message(cmd, retdata)


def set_computer_tags(request, name, uuid, o_computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    tags = data["set_computer_tags"]["tags"]
    all_id = Attribute.objects.get(
        property_att__prefix="SET",
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
        repositories = Repository.available_repos(o_computer, old_tags_id)
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
        repositories = Repository.available_repos(
            o_computer,
            new_tags_id + com_tags_id
        )
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


def check_computer(o_computer, name, version, ip, uuid):
    # registration of ip, version, uuid and Migration of computer
    o_version = Version.objects.get(name=version)

    if not o_computer:
        o_computer = Computer.objects.create(name, o_version, uuid)
        Migration.objects.create(o_computer, o_version)

        if settings.MIGASFREE_NOTIFY_NEW_COMPUTER:
            Notification.objects.create(
                "New Computer added id=[%s]: NAME=[%s] UUID=[%s]" % (
                    o_computer.id,
                    o_computer.__unicode__(),
                    o_computer.uuid
                )
            )

    # Check Migration
    if o_computer.version != o_version:
        Migration.objects.create(o_computer, o_version)

    notify_change_data_computer(o_computer, name, o_version, ip, uuid)

    o_computer.update_identification(name, o_version, uuid, ip)

    return o_computer


def notify_change_data_computer(o_computer, name, o_version, ip, uuid):
    if settings.MIGASFREE_NOTIFY_CHANGE_NAME and (o_computer.name != name):
        Notification.objects.create(
            "Computer id=[%s]: NAME [%s] changed by [%s]" % (
                o_computer.id,
                o_computer.__unicode__(),
                name
            )
        )

    if settings.MIGASFREE_NOTIFY_CHANGE_IP and (o_computer.ip != ip):
        if (o_computer.ip and ip):
            Notification.objects.create(
                "Computer id=[%s]: IP [%s] changed by [%s]" % (
                    o_computer.id,
                    o_computer.ip,
                    ip
                )
            )

    if settings.MIGASFREE_NOTIFY_CHANGE_UUID and (o_computer.uuid != uuid):
        Notification.objects.create(
            "Computer id=[%s]: UUID [%s] changed by [%s]" % (
                o_computer.id,
                o_computer.uuid,
                uuid
            )
        )


def create_repositories_package(packagename, versionname):
    o_version = Version.objects.get(name=versionname)
    try:
        package = Package.objects.get(name=packagename, version=o_version)
        qset = Repository.objects.filter(packages__id=package.id)
        for repo in qset:
            create_physical_repository(
                {},  # without request object
                repo,
                repo.packages.all().values_list('id', flat=True)
            )
    except:
        pass


def create_repositories_of_packageset(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    try:
        create_repositories_package(
            os.path.basename(data['packageset']),
            data['version']
        )
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
