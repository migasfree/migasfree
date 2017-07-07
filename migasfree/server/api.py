# -*- coding: utf-8 -*-

import os
import inspect

from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext as _

from .models import (
    Attribute, AttributeSet, Computer, BasicAttribute,
    Error, Fault, FaultDefinition, HwNode, Message,
    Migration, Notification, Package, Pms, Platform, Property,
    Deployment, Store, ServerAttribute, Synchronization, User,
    Project, Policy,
)
from .secure import get_keys_to_client, get_keys_to_packager
from .views import load_hw
from .tasks import create_repository_metadata
from .utils import (
    uuid_change_format, get_client_ip,
    list_difference, list_common, to_list,
    remove_duplicates_preserving_order,
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


def add_notification_project(project, pms, computer):
    Notification.objects.create(
        _("Project [%s] with P.M.S. [%s] registered by computer [%s].") % (
            '<a href="{}">{}</a>'.format(
                reverse('admin:server_project_change', args=(project.id,)),
                project
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
    except IndexError:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def upload_computer_software_base_diff(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        computer.update_software_inventory(data[cmd])
        ret = return_message(cmd, errmfs.ok())
    except IndexError:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def upload_computer_software_base(request, name, uuid, computer, data):
    """ DEPRECATED endpoint for migasfree-client >= 4.14 """
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    return return_message(cmd, errmfs.ok())


def upload_computer_software_history(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        computer.update_software_history(data[cmd])
        ret = return_message(cmd, errmfs.ok())
    except IndexError:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def get_computer_software(request, name, uuid, computer, data):
    """ DEPRECATED endpoint for migasfree-client >= 4.14 """
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    return return_message(
        cmd,
        ''  # deprecated field computer.version.base, empty for compatibility!!!
    )


def upload_computer_errors(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    try:
        Error.objects.create(computer, computer.project, data[cmd])

        ret = return_message(cmd, errmfs.ok())
    except IndexError:
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
            Synchronization.objects.create(computer)
        else:
            message.update_message(data[cmd])
        ret = return_message(cmd, errmfs.ok())
    except IndexError:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def return_message(cmd, data):
    return {'{}.return'.format(cmd): data}


def get_properties(request, name, uuid, computer, data):
    """
    First call of client requesting to server what it must do.
    The server responds a JSON:

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

    The client will eval the code in PROPERTIES and FAULTS and
    will upload it to server in a file called request.json
    calling to "post_request" view
    """

    return return_message(
        str(inspect.getframeinfo(inspect.currentframe()).function),
        {"properties": Property.enabled_client_properties()}
    )


def upload_computer_info(request, name, uuid, computer, data):
    """
    Process the file request.json and returns a JSON with:
        * fault definitions
        * repositories
        * packages
        * devices

        INPUT:
        =====
        A file "request.json" with the result of evaluate the request obtained
        by "get_request"

            {
                "computer": {
                    "hostname": HOSTNAME,
                    ["fqdn": FQDN,]
                    "ip": IP,
                    "platform": PLATFORM,
                    "version" | "project": VERSION/PROJECT,
                    "user": USER,
                    "user_fullname": USER_FULLNAME
                },
                "attributes":[{"name": VALUE}, ...]
            }

        OUTPUT:
        ======
        After of process this file, the server responds to client a JSON:

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

    computer_info = data.get(cmd).get("computer")
    platform_name = computer_info.get('platform', 'unknown')
    project_name = computer_info.get(
        'version',  # key is version for compatibility!!!
        computer_info.get(
            'project',
            'unknown'
        )
    )
    pms_name = computer_info.get(
        'pms',
        'apt-get'
    )
    fqdn = computer_info.get('fqdn', None)

    notify_platform = False
    notify_project = False

    # auto register Platform
    if not Platform.objects.filter(name=platform_name):
        if not settings.MIGASFREE_AUTOREGISTER:
            return return_message(
                cmd,
                errmfs.error(errmfs.CAN_NOT_REGISTER_COMPUTER)
            )

        # if all ok we add the platform
        Platform.objects.create(platform_name)

        notify_platform = True

    # auto register project
    if not Project.objects.filter(name=project_name):
        if not settings.MIGASFREE_AUTOREGISTER:
            return return_message(
                cmd,
                errmfs.error(errmfs.CAN_NOT_REGISTER_COMPUTER)
            )

        # if all ok, we add the project
        Project.objects.create(
            project_name,
            Pms.objects.get(name=pms_name),
            Platform.objects.get(name=platform_name),
            settings.MIGASFREE_AUTOREGISTER
        )

        notify_project = True

    try:
        client_attributes = data.get(cmd).get("attributes")  # basic and client attributes
        ip_address = computer_info.get("ip", "")
        forwarded_ip_address = get_client_ip(request)

        # IP registration, project and computer Migration
        computer = check_computer(
            computer,
            name,
            fqdn,
            project_name,
            ip_address,
            forwarded_ip_address,
            uuid,
        )

        project = Project.objects.get(name=project_name)

        if notify_platform:
            platform = Platform.objects.get(name=platform_name)
            add_notification_platform(platform, computer)

        if notify_project:
            pms = Pms.objects.get(name=pms_name)
            add_notification_project(project, pms, computer)

        # if not exists the user, we add it
        user, _ = User.objects.get_or_create(
            name=computer_info.get("user"),
            defaults={
                'fullname': computer_info.get("user_fullname", "")
            }
        )

        computer.update_sync_user(user)
        computer.sync_attributes.clear()

        computer.sync_attributes.add(
            *BasicAttribute.process(
                id=computer.id,
                ip_address=ip_address,
                project=computer.project.name,
                platform=computer.project.platform.name,
                user=user.name,
                description=computer.get_cid_description()
            )
        )

        # client attributes
        for prefix, value in client_attributes.iteritems():
            client_property = Property.objects.get(prefix=prefix)
            if client_property.sort == 'client':
                computer.sync_attributes.add(
                    *Attribute.process_kind_property(client_property, value)
                )

        # Tags (server attributes) (not running on clients!!!)
        for tag in computer.tags.all().filter(property_att__enabled=True):
            computer.sync_attributes.add(
                *Attribute.process_kind_property(tag.property_att, tag.value)
            )

        # AttributeSets
        computer.sync_attributes.add(*AttributeSet.process(computer.get_all_attributes()))

        fault_definitions = FaultDefinition.enabled_for_attributes(computer.get_all_attributes())

        lst_deploys = []
        lst_pkg_to_remove = []
        lst_pkg_to_install = []

        # deployments
        deploys = Deployment.available_deployments(computer, computer.get_all_attributes())
        for d in deploys:
            lst_deploys.append({"name": d.name})
            if d.packages_to_remove:
                for p in to_list(d.packages_to_remove):
                    if p != "":
                        lst_pkg_to_remove.append(p)
            if d.packages_to_install:
                for p in to_list(d.packages_to_install):
                    if p != "":
                        lst_pkg_to_install.append(p)

        # policies
        policy_pkg_to_install, policy_pkg_to_remove = Policy.get_packages(computer)
        lst_pkg_to_install.extend(policy_pkg_to_install)
        lst_pkg_to_remove.extend(policy_pkg_to_remove)

        # devices
        logical_devices = []
        for device in computer.logical_devices(computer.get_all_attributes()):
            logical_devices.append(device.as_dict(computer.project))

        default_logical_device = 0
        if computer.default_logical_device:
            default_logical_device = computer.default_logical_device.id

        # Hardware
        capture_hardware = True
        if computer.last_hardware_capture:
            capture_hardware = (datetime.now() > (
                computer.last_hardware_capture.replace(tzinfo=None) + timedelta(
                    days=settings.MIGASFREE_HW_PERIOD
                ))
            )

        # Finally, JSON creation
        data = {
            "faultsdef": fault_definitions,
            "repositories": lst_deploys,
            "packages": {
                "remove": remove_duplicates_preserving_order(lst_pkg_to_remove),
                "install": remove_duplicates_preserving_order(lst_pkg_to_install)
            },
            "devices": {
                "logical": logical_devices,
                "default": default_logical_device,
            },
            "base": False,  # computerbase and base has been removed!!!
            "hardware_capture": capture_hardware
        }

        ret = return_message(cmd, data)
    except ObjectDoesNotExist:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def upload_computer_faults(request, name, uuid, computer, data):
    """
    INPUT:
        'faults': {
            'name': 'result',
            ...
        }
    """

    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)
    faults = data.get(cmd).get("faults")

    try:
        for name, result in faults.iteritems():
            try:
                if result:
                    Fault.objects.create(
                        computer,
                        FaultDefinition.objects.get(name=name),
                        result
                    )
            except ObjectDoesNotExist:
                pass

        ret = return_message(cmd, {})
    except AttributeError:
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
    project_name = data.get('version', data.get('project', 'unknown'))  # key is version for compatibility!!!
    pms_name = data.get('pms', 'apt-get')
    fqdn = data.get('fqdn', None)

    notify_platform = False
    notify_project = False

    # auto register Platform
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

    # auto register project
    if not Project.objects.filter(name=project_name):
        if not settings.MIGASFREE_AUTOREGISTER:
            if not user or not user.has_perm("server.can_save_project"):
                return return_message(
                    cmd,
                    errmfs.error(errmfs.CAN_NOT_REGISTER_COMPUTER)
                )

        # if all ok we add the project
        Project.objects.create(
            project_name,
            Pms.objects.get(name=pms_name),
            Platform.objects.get(name=platform_name),
            settings.MIGASFREE_AUTOREGISTER
        )

        notify_project = True

    # REGISTER COMPUTER
    # Check project
    try:
        project = Project.objects.get(name=project_name)
        # if not auto register, check that the user can save computer
        if not project.auto_register_computers:
            if not user or not user.has_perm("server.can_save_computer"):
                return return_message(
                    cmd,
                    errmfs.error(errmfs.CAN_NOT_REGISTER_COMPUTER)
                )

        # Add Computer
        computer = check_computer(
            computer,
            name,
            fqdn,
            project_name,
            data.get('ip', ''),
            get_client_ip(request),
            uuid
        )

        if notify_platform:
            platform = Platform.objects.get(name=platform_name)
            add_notification_platform(platform, computer)

        if notify_project:
            pms = Pms.objects.get(name=pms_name)
            add_notification_project(project, pms, computer)

        # returns keys to client
        return return_message(cmd, get_keys_to_client(project_name))
    except ObjectDoesNotExist:
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

    project_name = data.get('version', data.get('project'))

    f = request.FILES["package"]
    filename = os.path.join(
        Store.path(project_name, data['store']),
        f.name
    )

    try:
        project = Project.objects.get(name=project_name)
    except ObjectDoesNotExist:
        return return_message(cmd, errmfs.error(errmfs.PROJECT_NOT_FOUND))

    store, _ = Store.objects.get_or_create(
        name=data['store'], project=project
    )

    save_request_file(f, filename)

    # we add the package
    if not data['source']:
        Package.objects.get_or_create(
            name=f.name,
            project=project,
            defaults={'store': store}
        )

    return return_message(cmd, errmfs.ok())


def upload_server_set(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    project_name = data.get('version', data.get('project'))

    f = request.FILES["package"]
    filename = os.path.join(
        Store.path(project_name, data['store']),
        data['packageset'],
        f.name
    )

    try:
        project = Project.objects.get(name=project_name)
    except ObjectDoesNotExist:
        return return_message(cmd, errmfs.error(errmfs.PROJECT_NOT_FOUND))

    store, _ = Store.objects.get_or_create(
        name=data['store'], project=project
    )

    # we add the package set and create the directory
    package, _ = Package.objects.get_or_create(
        name=data['packageset'],
        project=project,
        defaults={'store': store}
    )
    package.create_dir()

    save_request_file(f, filename)

    # if exists path, move it
    if "path" in data and data["path"] != "":
        dst = os.path.join(
            Store.path(project_name, data['store']),
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
    for deploy in Deployment.objects.filter(
        project=computer.project,
        enabled=True
    ):
        for tag in deploy.included_attributes.filter(
            property_att__sort='server',
            property_att__enabled=True
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
    all_id = Attribute.objects.get(pk=1).id  # All Systems attribute is the first one

    try:
        lst_tags_obj = []
        lst_tags_id = []
        for tag in data["set_computer_tags"]["tags"]:
            ltag = tag.split("-", 1)
            if len(ltag) > 1:
                attribute = ServerAttribute.objects.get(
                    property_att__prefix=ltag[0],
                    value=ltag[1]
                )
                lst_tags_obj.append(attribute)
                lst_tags_id.append(attribute.id)
        lst_tags_id.append(all_id)

        lst_computer_id = list(computer.tags.values_list('id', flat=True))
        lst_computer_id.append(all_id)

        old_tags_id = list_difference(lst_computer_id, lst_tags_id)
        new_tags_id = list_difference(lst_tags_id, lst_computer_id)
        com_tags_id = list_common(lst_computer_id, lst_tags_id)

        lst_pkg_remove = []
        lst_pkg_install = []
        lst_pkg_preinstall = []

        # old deployments
        for deploy in Deployment.available_deployments(computer, old_tags_id):
            # INVERSE !!!!
            lst_pkg_remove.extend(
                to_list(
                    "{} {} {}".format(
                        deploy.packages_to_install,
                        deploy.default_included_packages,
                        deploy.default_preincluded_packages
                    )
                )
            )

            lst_pkg_install.extend(
                to_list(
                    "{} {}".format(
                        deploy.packages_to_remove,
                        deploy.default_excluded_packages
                    )
                )
            )

        # new deployments
        for deploy in Deployment.available_deployments(
            computer,
            new_tags_id + com_tags_id
        ):
            lst_pkg_remove.extend(
                to_list(
                    "{} {}".format(
                        deploy.packages_to_remove,
                        deploy.default_excluded_packages
                    )
                )
            )

            lst_pkg_install.extend(
                to_list(
                    "{} {}".format(
                        deploy.packages_to_install,
                        deploy.default_included_packages
                    )
                )
            )

            lst_pkg_preinstall.extend(
                to_list(deploy.default_preincluded_packages)
            )

        ret_data = errmfs.ok()
        ret_data["packages"] = {
            "preinstall": lst_pkg_preinstall,
            "install": lst_pkg_install,
            "remove": lst_pkg_remove,
        }

        computer.tags = lst_tags_obj

        ret = return_message(cmd, ret_data)
    except ObjectDoesNotExist:
        ret = return_message(cmd, errmfs.error(errmfs.GENERIC))

    return ret


def check_computer(computer, name, fqdn, project_name, ip_address, forwarded_ip_address, uuid):
    # registration of IPs, project, uuid and Migration of a computer
    project = Project.objects.get(name=project_name)

    if not computer:
        computer = Computer.objects.create(name, project, uuid)
        Migration.objects.create(computer, project)

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

    if computer.project != project:
        Migration.objects.create(computer, project)

    notify_change_data_computer(computer, name, ip_address, uuid)

    computer.update_identification(name, fqdn, project, uuid, ip_address, forwarded_ip_address)

    return computer


def notify_change_data_computer(computer, name, ip_address, uuid):
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

    if settings.MIGASFREE_NOTIFY_CHANGE_IP and computer.ip_address != ip_address:
        if computer.ip_address and ip_address:
            Notification.objects.create(
                _("Computer id=[%s]: IP [%s] changed by [%s]") % (
                    '<a href="{}">{}</a>'.format(
                        reverse('admin:server_computer_change', args=(computer.id,)),
                        computer.id
                    ),
                    computer.ip_address,
                    ip_address
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


def create_repositories_package(package_name, project_name):
    try:
        project = Project.objects.get(name=project_name)
        package = Package.objects.get(name=package_name, project=project)
        for deploy in Deployment.objects.filter(available_packages__id=package.id):
            create_repository_metadata(deploy)
    except ObjectDoesNotExist:
        pass


def create_repositories_of_packageset(request, name, uuid, computer, data):
    cmd = str(inspect.getframeinfo(inspect.currentframe()).function)

    project_name = data.get('version', data.get('project'))

    try:
        create_repositories_package(
            os.path.basename(data['packageset']),
            project_name
        )
        ret = return_message(cmd, errmfs.ok())
    except KeyError:
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
