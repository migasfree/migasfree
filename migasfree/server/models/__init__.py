# -*- coding: utf-8 -*-

# import order is very important!!!

from migasfree.server.models.common import LANGUAGES_CHOICES

from migasfree.server.models.user import User
from migasfree.server.models.query import Query, get_query_names
from migasfree.server.models.checking import Checking
from migasfree.server.models.autocheck_error import AutoCheckError


from migasfree.server.models.pms import Pms
from migasfree.server.models.property import Property

from migasfree.server.models.platform import Platform
from migasfree.server.models.version import Version, get_version_names
from migasfree.server.models.attribute import Attribute

from migasfree.server.models.device_type import DeviceType
from migasfree.server.models.device_manufacturer import DeviceManufacturer
from migasfree.server.models.device_connection import DeviceConnection
from migasfree.server.models.device_model import DeviceModel
from migasfree.server.models.device_feature import DeviceFeature
from migasfree.server.models.device_driver import DeviceDriver
from migasfree.server.models.device import Device
from migasfree.server.models.device_logical import DeviceLogical


from migasfree.server.models.message_server import MessageServer
from migasfree.server.models.computer import Computer

from migasfree.server.models.login import Login
from migasfree.server.models.update import Update
from migasfree.server.models.hw_node import HwNode

from migasfree.server.models.notification import Notification
from migasfree.server.models.message import Message
from migasfree.server.models.error import Error
from migasfree.server.models.fault_def import FaultDef
from migasfree.server.models.fault import Fault
from migasfree.server.models.migration import Migration

from migasfree.server.models.hw_capability import HwCapability
from migasfree.server.models.hw_configuration import HwConfiguration
from migasfree.server.models.hw_logical_name import HwLogicalName

from migasfree.server.models.schedule import Schedule
from migasfree.server.models.schedule_delay import ScheduleDelay

from migasfree.server.models.version_manager import VersionManager, \
    UserProfile, user_version
from migasfree.server.models.store import Store
from migasfree.server.models.package import Package
from migasfree.server.models.repository import Repository
