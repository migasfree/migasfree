# -*- coding: utf-8 -*-

import os
import inspect

from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.conf import settings
from django.utils import timezone, dateformat
from django.utils.translation import ugettext as _

from .models import (
    LANGUAGES_CHOICES, Attribute, AttributeSet, ClientProperty, Computer,
    Error, Fault, FaultDef, Feature, HwNode, Message,
    Migration, Notification, Login, Package, Pms, Platform, Property,
    Repository, Store, Tag, Update, User, Version,
)
from .security import get_keys_to_client, get_keys_to_packager
from .views import load_hw
from .tasks import create_physical_repository
from .functions import (
    uuid_change_format,
    list_difference, list_common,
)
from . import errmfs

import logging
logger = logging.getLogger('migasfree')


def add_notification_platform(platform, computer):
    Notification.objects.create(
        _("Platform [%s] registered by computer [%s].") % (
            '<a href="{}">{}</a>'.format(
                reverse('admin:server_platform_change', args=(platform.id,)),
                platform
            ),
            '<a href="{}">{}</a>'.format(
                reverse('admin:server_computer_change', args=(computer.id,)),
                computer
            )
        )
    )


def add_notification_version(version, pms, computer):
    Notification.objects.create(
        _("Version [%s] with P.M.S. [%s] registered by computer [%s].") % (
            '<a href="{}">{}</a>'.format(
                reverse('admin:server_version_change', args=(version.id,)),
                version
            ),
            '<a href="{}">{}</a>'.format(
                reverse('admin:server_pms_change', args=(pms.id,)),
                pms
            ),
            '<a href="{}">{}</a>'.format(
                reverse('admin:server_computer_change', args=(computer.id,)),
                computer
            )
        )
    )


def get_computer(name, uuid):
    """
    Returns a computer object (or None if not found)
    """
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

    # DEPRECATED This Block. Only for compatibility with client <= 2
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
            except (
                Computer.DoesNotExist,
                Computer.MultipleObjectsReturned
            ):
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
        computer.update_hardware_resume()
        ret = return_message(cmd, errmfs.ok())
    except:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def upload_computer_software_base_diff(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        computer.update_software_inventory(data[cmd])
        ret = return_message(cmd, errmfs.ok())
    except:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def upload_computer_software_base(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        version = Version.objects.get(pk=computer.version_id)
        version.update_base(data[cmd])

        ret = return_message(cmd, errmfs.ok())
    except:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def upload_computer_software_history(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        computer.update_software_history(data[cmd])
        ret = return_message(cmd, errmfs.ok())
    except:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def get_computer_software(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        ret = return_message(
            cmd,
            computer.version.base
        )
    except:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def upload_computer_errors(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        Error.objects.create(computer, computer.version, data[cmd])

        ret = return_message(cmd, errmfs.ok())
    except:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def upload_computer_message(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    if not computer:
        return return_message(cmd, errmfs.error(errmfs.COMPUTER_NOT_FOUND))

    try:
        message = Message.objects.get(computer=computer)
        if data[cmd] == "":
            message.delete()
    except ObjectDoesNotExist:
        message = Message(computer=computer)

    try:
        if data[cmd] == "":
            Update.objects.create(computer)
        else:
            message.update_message(data[cmd])
        ret = return_message(cmd, errmfs.ok())
    except:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def return_message(cmd, data):
    return {'{}.return'.format(cmd): data}


def get_properties(request, name, uuid, computer, data):
    """
    First call of client requesting to server what it must do.
    The server responds a json:

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
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def upload_computer_info(request, name, uuid, computer, data):
    """
    Process the file request.json and return a json with the faultsdef,
    repositories, packages and devices
        INPUT:
        =====
        A file "request.json" with the result of evaluate the request obtained
        by "get_request"

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
        After of process this file the server responds to client a json:

            {
                "faultsdef": [
                    {
                        "name":"NAME",
                        "function":"CODE",
                        "language": "LANGUAGE"
                    },
                    ...
                ],
                "repositories": [ {"name": "REPONAME" }, ...],
                "packages": {
                    "install": ["pkg1","pkg2","pkg3", ...],
                    "remove": ["pkg1","pkg2","pkg3", ...]
                } ,
                "base": true|false,
                "hardware_capture": true|false,
                "devices": {
                    "logical": [object1, object2, ...],
                    "default": int
                }
            }
    """

    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    platform_name = data.get("upload_computer_info").get("computer").get(
        'platform',
        'unknown'
    )
    version_name = data.get("upload_computer_info").get("computer").get(
        'version',
        'unknown'
    )
    pms_name = data.get("upload_computer_info").get("computer").get(
        'pms',
        'apt-get'
    )

    notify_platform = False
    notify_version = False

    # Autoregister Platform
    if not Platform.objects.filter(name=platform_name):
        if not settings.MIGASFREE_AUTOREGISTER:
            return return_message(
                cmd,
                errmfs.error(errmfs.CAN_NOT_REGISTER_COMPUTER)
            )

        # if all ok we add the platform
        Platform.objects.create(platform_name)

        notify_platform = True

    # Autoregister Version
    if not Version.objects.filter(name=version_name):
        if not settings.MIGASFREE_AUTOREGISTER:
            return return_message(
                cmd,
                errmfs.error(errmfs.CAN_NOT_REGISTER_COMPUTER)
            )

        # if all ok, we add the version
        Version.objects.create(
            version_name,
            Pms.objects.get(name=pms_name),
            Platform.objects.get(name=platform_name),
            settings.MIGASFREE_AUTOREGISTER
        )

        notify_version = True

    lst_attributes = []  # List of attributes of computer

    try:
        dic_computer = data.get("upload_computer_info").get("computer")
        properties = data.get("upload_computer_info").get("attributes")

        # 1.- PROCESS COMPUTER
        # registration of ip, version an Migration of computer
        computer = check_computer(
            computer,
            name,
            version_name,
            dic_computer.get("ip", ""),
            uuid,
        )

        # Get version
        version = Version.objects.get(name=version_name)

        if notify_platform:
            platform = Platform.objects.get(name=platform_name)
            add_notification_platform(platform, computer)

        if notify_version:
            pms = Pms.objects.get(name=pms_name)
            add_notification_version(version, pms, computer)

        # if not exists the user, we add it
        user, _ = User.objects.get_or_create(
            name=dic_computer.get("user"),
            defaults={
                'fullname': dic_computer.get("user_fullname", "")
            }
        )

        # Save Login
        login, created = Login.objects.get_or_create(
            computer=computer,
            defaults={
                'user': user,
                'date': dateformat.format(timezone.now(), 'Y-m-d H:i:s')
            }
        )
        if not created:
            login.update_user(user)

        login.attributes.clear()

        # 2.- PROCESS PROPERTIES
        for e in properties:
            o_property = ClientProperty.objects.get(prefix=e)
            value = properties.get(e)
            for att in Attribute.process_kind_property(o_property, value):
                login.attributes.add(att)
                lst_attributes.append(att)

        # ADD Tags (not running on clients!!!)
        for tag in computer.tags.all().filter(property_att__active=True):
            for att in Attribute.process_kind_property(
                tag.property_att,
                tag.value
            ):
                login.attributes.add(att)
                lst_attributes.append(att)

        # ADD ATTRIBUTE CID (not running on clients!!!)
        try:
            prp_cid = Property.objects.get(prefix="CID", active=True)
            if prp_cid:
                cid_description = computer.get_cid_description()
                cid = Feature.objects.create(
                    prp_cid,
                    "%s~%s" % (str(computer.id), cid_description)
                )
                login.attributes.add(cid)
                lst_attributes.append(cid.id)

                cid.update_description(cid_description)
        except:
            pass

        # ADD AttributeSets
        lst_set = AttributeSet.process(lst_attributes)
        if lst_set:
            for item in lst_set:
                login.attributes.add(item)

        # 3 FaultsDef
        lst_faultsdef = []
        for d in FaultDef.enabled_for_attributes(lst_attributes):
            lst_faultsdef.append({
                "language": LANGUAGES_CHOICES[d['language']][1],
                "name": d['name'],
                "code": d['code']
            })

        repositories = Repository.available_repos(computer, lst_attributes)

        # 4.- CREATE JSON
        lst_repos = []
        lst_pkg_remove = []
        lst_pkg_install = []

        for r in repositories:
            lst_repos.append({"name": r.name})
            if r.toremove:
                for p in r.toremove.replace("\n", " ").split(" "):
                    if p != "":
                        lst_pkg_remove.append(p)
            if r.toinstall:
                for p in r.toinstall.replace("\n", " ").split(" "):
                    if p != "":
                        lst_pkg_install.append(p)

        # DEVICES
        logical_devices = []
        for device in computer.logical_devices(lst_attributes):
            logical_devices.append(device.as_dict(computer.version))

        if computer.default_logical_device:
            default_logical_device = computer.default_logical_device.id
        else:
            default_logical_device = 0

        # Hardware
        capture_hardware = True
        if computer.datehardware:
            capture_hardware = (datetime.now() > (
                computer.datehardware.replace(tzinfo=None) + timedelta(
                    days=settings.MIGASFREE_HW_PERIOD
                ))
            )

        data = {
            "faultsdef": lst_faultsdef,
            "repositories": lst_repos,
            "packages": {
                "remove": lst_pkg_remove,
                "install": lst_pkg_install
            },
            "devices": {
                "logical": logical_devices,
                "default": default_logical_device,
            },
            "base": version.computerbase == computer.__str__(),
            "hardware_capture": capture_hardware
        }

        ret = return_message(cmd, data)
    except:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def upload_computer_faults(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    faults = data.get(cmd).get("faults")
    version = Version.objects.get(id=computer.version_id)

    try:
        # PROCESS FAULTS
        for f in faults:
            try:
                msg = faults.get(f)
                if msg != "":
                    Fault.objects.create(
                        computer,
                        version,
                        FaultDef.objects.get(name=f),
                        msg
                    )
            except:
                pass

        ret = return_message(cmd, {})
    except:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    logger.debug('upload_computer_faults ret: %s' % ret)
    return ret


def upload_devices_changes(request, name, uuid, computer, data):
    """ DEPRECATED endpoint for migasfree-client >= 4.13 """
    logger.debug('upload_devices_changes data: %s' % data)
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    return return_message(cmd, errmfs.ok())


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
                return return_message(
                    cmd,
                    errmfs.error(errmfs.CAN_NOT_REGISTER_COMPUTER)
                )

        # if all ok we add the platform
        Platform.objects.create(platform_name)

        notify_platform = True

    # Autoregister Version
    if not Version.objects.filter(name=version_name):
        if not settings.MIGASFREE_AUTOREGISTER:
            if not user or not user.has_perm("server.can_save_version"):
                return return_message(
                    cmd,
                    errmfs.error(errmfs.CAN_NOT_REGISTER_COMPUTER)
                )

        # if all ok we add the version
        Version.objects.create(
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
                return return_message(
                    cmd,
                    errmfs.error(errmfs.CAN_NOT_REGISTER_COMPUTER)
                )

        # ALL IS OK
        # 1.- Add Computer
        computer = check_computer(
            computer,
            name,
            version_name,
            data.get('ip', ''),
            uuid
        )

        if notify_platform:
            platform = Platform.objects.get(name=platform_name)
            add_notification_platform(platform, computer)

        if notify_version:
            pms = Pms.objects.get(name=pms_name)
            add_notification_version(version, pms, computer)

        # 2.- returns keys to client
        return return_message(cmd, get_keys_to_client(version_name))
    except:
        return return_message(
            cmd,
            errmfs.error(errmfs.USER_DOES_NOT_HAVE_PERMISSION)
        )


def get_key_packager(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    user = auth.authenticate(
        username=data['username'],
        password=data['password']
    )
    if not user.has_perm("server.can_save_package"):
        return return_message(
            cmd,
            errmfs.error(errmfs.CAN_NOT_REGISTER_COMPUTER)
        )

    return return_message(cmd, get_keys_to_packager())


def upload_server_package(request, name, uuid, computer, data):
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
        version = Version.objects.get(name=data['version'])
    except ObjectDoesNotExist:
        return return_message(cmd, errmfs.error(errmfs.VERSION_NOT_FOUND))

    store, _ = Store.objects.get_or_create(
        name=data['store'], version=version
    )

    save_request_file(f, filename)

    # we add the package
    if not data['source']:
        Package.objects.get_or_create(
            name=f.name,
            version=version,
            defaults={'store': store}
        )

    return return_message(cmd, errmfs.ok())


def upload_server_set(request, name, uuid, computer, data):
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
        version = Version.objects.get(name=data['version'])
    except ObjectDoesNotExist:
        return return_message(cmd, errmfs.error(errmfs.VERSION_NOT_FOUND))

    store, _ = Store.objects.get_or_create(
        name=data['store'], version=version
    )

    # we add the package set and create the directory
    o_package, _ = Package.objects.get_or_create(
        name=data['packageset'],
        version=version,
        defaults={'store': store}
    )
    o_package.create_dir()

    save_request_file(f, filename)

    # if exists path move it
    if "path" in data and data["path"] != "":
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
        except OSError:
            pass
        os.rename(filename, dst)

    return return_message(cmd, errmfs.ok())


def get_computer_tags(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    selected_tags = []
    for tag in computer.tags.all():
        selected_tags.append(tag.__str__())

    available_tags = {}
    for rps in Repository.objects.filter(
        version=computer.version,
        active=True
    ):
        for tag in rps.attributes.filter(
            property_att__tag=True,
            property_att__active=True
        ):
            if tag.property_att.name not in available_tags:
                available_tags[tag.property_att.name] = []

            value = tag.__str__()
            if value not in available_tags[tag.property_att.name]:
                available_tags[tag.property_att.name].append(value)

    ret = errmfs.ok()
    ret['available'] = available_tags
    ret['selected'] = selected_tags

    return return_message(cmd, ret)


def set_computer_tags(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    all_id = Attribute.objects.get(
        property_att__prefix="SET",
        value="ALL SYSTEMS"
    ).id

    try:
        lst_tags_obj = []
        lst_tags_id = []
        for tag in data["set_computer_tags"]["tags"]:
            ltag = tag.split("-", 1)
            if len(ltag) > 1:
                o_attribute = Tag.objects.get(
                    property_att__prefix=ltag[0],
                    value=ltag[1]
                )
                lst_tags_obj.append(o_attribute)
                lst_tags_id.append(o_attribute.id)
        lst_tags_id.append(all_id)

        lst_computer_id = computer.tags.values_list('id', flat=True)
        lst_computer_id.append(all_id)

        old_tags_id = list_difference(lst_computer_id, lst_tags_id)
        new_tags_id = list_difference(lst_tags_id, lst_computer_id)
        com_tags_id = list_common(lst_computer_id, lst_tags_id)

        lst_pkg_remove = []
        lst_pkg_install = []
        lst_pkg_preinstall = []

        # old repositories
        for r in Repository.available_repos(computer, old_tags_id):
            # INVERSE !!!!
            pkgs = "{} {} {}".format(
                r.toinstall,
                r.defaultinclude,
                r.defaultpreinclude
            ).replace("\r", " ").replace("\n", " ")
            for p in pkgs.split():
                if p != "" and p != 'None':
                    lst_pkg_remove.append(p)

            pkgs = "{} {}".format(
                r.toremove,
                r.defaultexclude
            ).replace("\r", " ").replace("\n", " ")
            for p in pkgs.split():
                if p != "" and p != 'None':
                    lst_pkg_install.append(p)

        # new repositories
        for r in Repository.available_repos(
            computer,
            new_tags_id + com_tags_id
        ):
            pkgs = "{} {}".format(
                r.toremove,
                r.defaultexclude
            ).replace("\r", " ").replace("\n", " ")
            for p in pkgs.split():
                if p != "" and p != 'None':
                    lst_pkg_remove.append(p)

            pkgs = "{} {}".format(
                r.toinstall,
                r.defaultinclude
            ).replace("\r", " ").replace("\n", " ")
            for p in pkgs.split():
                if p != "" and p != 'None':
                    lst_pkg_install.append(p)

            pkgs = r.defaultpreinclude.replace("\r", " ").replace("\n", " ")
            for p in pkgs.split():
                if p != "" and p != 'None':
                    lst_pkg_preinstall.append(p)

        ret_data = errmfs.ok()
        ret_data["packages"] = {
            "preinstall": lst_pkg_preinstall,
            "install": lst_pkg_install,
            "remove": lst_pkg_remove,
        }

        computer.tags = lst_tags_obj

        ret = return_message(cmd, ret_data)
    except:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def check_computer(computer, name, version_name, ip, uuid):
    # registration of ip, version, uuid and Migration of a computer
    version = Version.objects.get(name=version_name)

    if not computer:
        computer = Computer.objects.create(name, version, uuid)
        Migration.objects.create(computer, version)

        if settings.MIGASFREE_NOTIFY_NEW_COMPUTER:
            Notification.objects.create(
                _("New Computer added id=[%s]: NAME=[%s] UUID=[%s]") % (
                    computer.id,
                    '<a href="{}">{}</a>'.format(
                        reverse('admin:server_computer_change', args=(computer.id,)),
                        computer
                    ),
                    computer.uuid
                )
            )

    if computer.version != version:
        Migration.objects.create(computer, version)

    notify_change_data_computer(computer, name, version, ip, uuid)

    computer.update_identification(name, version, uuid, ip)

    return computer


def notify_change_data_computer(computer, name, version, ip, uuid):
    if settings.MIGASFREE_NOTIFY_CHANGE_NAME and (computer.name != name):
        Notification.objects.create(
            _("Computer id=[%s]: NAME [%s] changed by [%s]") % (
                '<a href="{}">{}</a>'.format(
                    reverse('admin:server_computer_change', args=(computer.id,)),
                    computer.id
                ),
                computer,
                name
            )
        )

    if settings.MIGASFREE_NOTIFY_CHANGE_IP and computer.ip != ip:
        if computer.ip and ip:
            Notification.objects.create(
                _("Computer id=[%s]: IP [%s] changed by [%s]") % (
                    '<a href="{}">{}</a>'.format(
                        reverse('admin:server_computer_change', args=(computer.id,)),
                        computer.id
                    ),
                    computer.ip,
                    ip
                )
            )

    if settings.MIGASFREE_NOTIFY_CHANGE_UUID and computer.uuid != uuid:
        Notification.objects.create(
            _("Computer id=[%s]: UUID [%s] changed by [%s]") % (
                '<a href="{}">{}</a>'.format(
                    reverse('admin:server_computer_change', args=(computer.id,)),
                    computer.id
                ),
                computer.uuid,
                uuid
            )
        )


def create_repositories_package(package_name, version_name):
    try:
        version = Version.objects.get(name=version_name)
        package = Package.objects.get(name=package_name, version=version)
        for repo in Repository.objects.filter(packages__id=package.id):
            create_physical_repository(repo)
    except ObjectDoesNotExist:
        pass


def create_repositories_of_packageset(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    try:
        create_repositories_package(
            os.path.basename(data['packageset']),
            data['version']
        )
        ret = return_message(cmd, errmfs.ok())
    except:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def save_request_file(archive, target):
    fp = open(target, 'wb+')
    for chunk in archive.chunks():
        fp.write(chunk)
    fp.close()

    try:
        # https://docs.djangoproject.com/en/dev/topics/http/file-uploads/
        # Files with: Size > FILE_UPLOAD_MAX_MEMORY_SIZE  -> generate a file
        # called something like /tmp/tmpzfp6I6.upload.
        # We remove it
        os.remove(archive.temporary_file_path())
    except (OSError, AttributeError):
        pass
