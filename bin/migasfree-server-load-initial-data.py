#!/usr/bin/python
# -*- coding: UTF-8 -*-
#pylint: disable-msg=C0103

import os
import sys
from datetime import datetime

from django.utils.translation import ugettext as _
from django.contrib.auth.models import Group, Permission

import migasfree

from migasfree.server.models import *

def create_pms():
    """
    PACKAGE MANAGEMENT SYSTEM
    """
    opms = Pms()
    opms.name = "yum"
    opms.createrepo = \
"""_DIRECTORY=%PATH%/%REPONAME%
rm -rf $_DIRECTORY/repodata
rm -rf $_DIRECTORY/checksum
createrepo -c checksum $_DIRECTORY
"""

    opms.repository = \
"""[%REPO%]
name=%REPO%
baseurl=http://$MIGASFREE_SERVER/repo/%VERSION%/REPOSITORIES/%REPO%
gpgcheck=0
enabled=1
http_caching=none
metadata_expire=1
"""

    opms.info = \
"""echo ****INFO****
rpm -qp --info $PACKAGE
echo
echo
echo ****REQUIRES****
rpm -qp --requires $PACKAGE
echo
echo
echo ****PROVIDES****
rpm -qp --provides $PACKAGE
echo
echo
echo ****OBSOLETES****
rpm -qp --obsoletes $PACKAGE
echo
echo
echo ****SCRIPTS****
rpm -qp --scripts $PACKAGE
echo
echo
echo ****CHANGELOG****
rpm -qp --changelog $PACKAGE
echo
echo
echo ****FILES****
rpm -qp --list $PACKAGE
echo
"""
    opms.save()
    print "Package Management System (added yum)"

    opms = Pms()
    opms.name = "zypper"
    opms.createrepo = \
"""_DIRECTORY=%PATH%/%REPONAME%
rm -rf $_DIRECTORY/repodata
rm -rf $_DIRECTORY/checksum
createrepo -c checksum $_DIRECTORY
"""

    opms.repository = \
"""[%REPO%]
name=%REPO%
baseurl=http://$MIGASFREE_SERVER/repo/%VERSION%/REPOSITORIES/%REPO%
gpgcheck=0
enabled=1
http_caching=none
metadata_expire=1
"""

    opms.info = \
"""
echo ****INFO****
rpm -qp --info $PACKAGE
echo
echo
echo ****REQUIRES****
rpm -qp --requires $PACKAGE
echo
echo
echo ****PROVIDES****
rpm -qp --provides $PACKAGE
echo
echo
echo ****OBSOLETES****
rpm -qp --obsoletes $PACKAGE
echo
echo
echo ****SCRIPTS****
rpm -qp --scripts $PACKAGE
echo
echo
echo ****CHANGELOG****
rpm -qp --changelog $PACKAGE
echo
echo
echo ****FILES****
rpm -qp --list $PACKAGE
echo
"""
    opms.save()
    print "Package Management System (added zypper)"

    opms = Pms()
    opms.name = "apt"
    opms.slug = "REPOSITORIES/dists"

    opms.createrepo = \
"""cd %PATH%
mkdir -p %REPONAME%/PKGS/binary-i386/
mkdir -p %REPONAME%/PKGS/sources/
cd ..
dpkg-scanpackages dists/%REPONAME%/PKGS /dev/null | gzip -9c > dists/%REPONAME%/PKGS/binary-i386/Packages.gz
dpkg-scansources dists/%REPONAME%/PKGS /dev/null | gzip -9c > dists/%REPONAME%/PKGS/sources/Sources.gz
"""

    opms.repository = \
"""deb http://$MIGASFREE_SERVER/repo/%VERSION%/REPOSITORIES %REPO% PKGS
"""
    opms.info = \
"""echo ****INFO****
dpkg -I $PACKAGE
echo
echo
echo ****REQUIRES****
dpkg-deb --showformat='${Depends}\n' --show $PACKAGE
echo
echo
echo ****PROVIDES****
dpkg-deb --showformat='${Provides}\n' --show $PACKAGE
echo
echo
echo ****OBSOLETES****
dpkg-deb --showformat='${Replaces}\n' --show $PACKAGE
echo
echo
echo "****SCRIPT PREINST****"
#dpkg-deb --showformat='${Source}' --show $PACKAGE
dpkg-deb -I $PACKAGE preinst
echo
echo
echo "****SCRIPT POSTINST****"
dpkg-deb -I $PACKAGE postinst
echo
echo
echo "****SCRIPT PRERM****"
dpkg-deb -I $PACKAGE prerm
echo
echo
echo "****SCRIPT POSTRM****"
dpkg-deb -I $PACKAGE postrm
echo
echo
echo ****CHANGELOG****
_DIR="/tmp/changelog"
_NAME=`dpkg-deb --showformat='${Package}' --show $PACKAGE`
dpkg -X $PACKAGE $_DIR > /dev/null
gzip -d $_DIR/usr/share/doc/$_NAME/changelog.Debian.gz
cat $_DIR/usr/share/doc/$_NAME/changelog.Debian
rm -r $_DIR
echo
echo
echo ****FILES****
dpkg-deb -c $PACKAGE | awk '{print $6}'
"""
    opms.save()
    print "Package Management System (add apt)"


def create_checkings():
    """
    Insert docstring here
    """
    ochecking = Checking()
    ochecking.name = _("Errors to check")
    ochecking.description = "Errors not marked as checked. You must mark the error as checked when the error is solutioned."
    ochecking.code = \
"""from migasfree.server.models import Error
result = Error.objects.filter(checked__exact=0).count()
url = '/migasfree/admin/server/error/?checked__exact=0'
icon = 'error.png'
msg = 'Errors to check'
"""
    ochecking.save()

    ochecking = Checking()
    ochecking.name = _("Faults to check")
    ochecking.description = "Faults not marked as checked. You must mark the fault as checked when the fault is solutioned"
    ochecking.code = \
"""from migasfree.server.models import Fault
result = Fault.objects.filter(checked__exact=0).count()
url = '/migasfree/admin/server/fault/?checked__exact=0'
icon = 'fault.png'
msg = 'Faults to check'
"""
    ochecking.save()

    ochecking = Checking()
    ochecking.name = _("Package/Set orphan")
    ochecking.description = "Packages that not have been asigned to a Repository."
    ochecking.code = \
"""from migasfree.server.models import Package
result = Package.objects.version(0).filter(Q(repository__id__exact=None)).count()
url = '/migasfree/query/?id=5'
icon = 'information.png'
msg = 'Package/Set orphan'
"""
    ochecking.save()

    ochecking = Checking()
    ochecking.name = _("Repositories files creation")
    ochecking.description = "Check if the current user version have to create the files of repositories (only will be created when in a Repository you change the packackes)"
    ochecking.code = \
"""from migasfree.server.models import Repository
from migasfree.server.functions import compare_values
result = 0
ds = Repository.objects.all()
for d in ds:
    if not compare_values(d.packages.values('id'), d.createpackages.values('id')):
            result = result+1
            url = '/migasfree/createrepositories'
            icon = 'repository.png'
            msg = 'Repositories files creation'
"""
    ochecking.save()

    ochecking = Checking()
    ochecking.name = _("Computer updating now")
    ochecking.description = "Check how many computers are being updated at this time"
    ochecking.code = \
"""from migasfree.settings import MIGASFREE_SECONDS_MESSAGE_ALERT
from datetime import datetime
from datetime import timedelta
url = '/migasfree/queryMessage'
msg = 'Computer updating now'
t = datetime.now() - timedelta(0, MIGASFREE_SECONDS_MESSAGE_ALERT)
result=Message.objects.all().count()-Message.objects.filter(date__lt=t).count()
icon = 'computer.png'
"""
    ochecking.save()
    
    ochecking = Checking()
    ochecking.name = _("Computer delayed")
    ochecking.description = "Check how many computers are delayed"
    ochecking.code = \
"""from migasfree.settings import MIGASFREE_SECONDS_MESSAGE_ALERT
from datetime import datetime
from datetime import timedelta
url = '/migasfree/queryMessage'
msg = 'Computer delayed' 
t = datetime.now() - timedelta(0, MIGASFREE_SECONDS_MESSAGE_ALERT)
result = Message.objects.filter(date__lt=t).count()
icon = 'computer_alert.png'
"""
    ochecking.save()    

    ochecking = Checking()
    ochecking.name = _("Server Messages")
    ochecking.description = "Server Messages"
    ochecking.code = \
"""
oMessages = MessageServer.objects.all()
result = oMessages.count()
url = '/migasfree/queryMessageServer'
msg = 'process run in server'
icon = 'spinner.gif'
"""
    ochecking.save()

def create_properties():
    """
    Insert docstring here
    """
    oproperty = Property()
    oproperty.prefix = "ALL"
    oproperty.code = "echo \"ALL SYSTEMS\"\n"
    oproperty.name = "ALL SYSTEMS"
    oproperty.save()
    print "Property (add ALL)"

    oproperty = Property()
    oproperty.prefix = "IP"
    oproperty.code =\
"""
import migasfree_client.network
print migasfree_client.network.get_network_info()['ip']
"""
    oproperty.name = "IP ADDRESS"
    oproperty.language = 1 # python
    oproperty.active = False
    oproperty.save()
    print "Property (add IP ADDRESS)"

    oproperty = Property()
    oproperty.prefix = "NET"
    oproperty.code = \
"""
import migasfree_client.network
print migasfree_client.network.get_network_info()['net']
"""
    oproperty.language = 1 # python
    oproperty.before_insert = "#Convert the IP address in the network address"
    oproperty.name = "NET"
    oproperty.active = False
    oproperty.save()
    print "Property (add NET)"

    oproperty = Property()
    oproperty.prefix = "GRP"
    oproperty.code = "echo \"GRP-AU,GRP-Administradores,GRP-Impresoras\"\n"
    oproperty.name = "LDAP GROUP"
    oproperty.kind = "-"
    oproperty.save()
    print "Property (add LDAP GROUP)"

    """
    oproperty = Property()
    oproperty.prefix = "CTX"
    oproperty.code = "echo RYS.AYTOZAR\n"
    oproperty.name = "LDAP CONTEXT"
    oproperty.kind = "R"
    oproperty.save()
    print "Property (add LDAP CONTEXT)"
    """

    oproperty = Property()
    oproperty.prefix = "HST"
    oproperty.code = "echo $HOSTNAME\n"
    oproperty.name = "MACHINE NAME"
    oproperty.save()
    print "Property (add MACHINE NAME)"

    oproperty = Property()
    oproperty.prefix = "PCI"
    oproperty.code = \
"""r=''
if [ `lspci -n | sed -n 1p | awk '{print $2}'` = 'Class' ]
then
    dev=`lspci -n |awk '{print $4}'`
else
    dev=`lspci -n |awk '{print $3}'`
fi
for l in $dev
do
    n=`lspci -d $l | awk '{for (i = 2; i <=NF;++i) print $i}' | tr \"\\n\" \" \" | sed 's/,//g'`
    r=\"$r$l~$n,\"
done
echo $r
"""
    oproperty.name = "DEVICE PCI"
    oproperty.kind = "-"
    oproperty.save()
    print "Property (add DEVICE PCI)"

    oproperty = Property()
    oproperty.prefix = "USR"
    oproperty.code = \
"""
import migasfree_client.utils
print migasfree_client.utils.get_current_user()
"""
    oproperty.name = "USER"
    oproperty.active = False
    oproperty.language = 1 # python
    oproperty.save()
    print "Property (add USER)"

    oproperty = Property()
    oproperty.prefix = "VRS"
    oproperty.code = \
"""
import migasfree_client.utils
print migasfree_client.utils.get_mfc_version()
"""
    oproperty.name = "VERSION"
    oproperty.active = False
    oproperty.language = 1 # python
    oproperty.save()
    print "Property (add VERSION)"

def create_faultdefs():
    """
    Insert docstring here
    """
    ofaultdef = FaultDef()
    ofaultdef.name = "LOW SYSTEM PARTITION SPACE"
    ofaultdef.description = "add a fault when the space in partition of system is low"
    ofaultdef.code = \
"""limite=15 #PORCENTAJE DE USO EN PARTICION /
DEVICE=`mount |grep \" on / \"|awk '{print $1}'`
usado=`df -Pl | grep $DEVICE | awk '{print $5}' | awk 'BEGIN {FS=\"%\";} {print $1}'`
if [ $usado -gt $limite ]
then
  echo \"El espacio usado en la particion de sistema $DEVICE es de un $usado%, superando el limite establecido en $limite% \"
  echo \"*** ACCIONES A REALIZAR ***\"
  echo \"Comprobar y Borrar archivos\"
  echo \"Ampliacion de la particion o cambio del Disco Duro\"
fi
"""
    ofaultdef.save()
    print "FaultDef (add LOW SYSTEM PARTITION SPACE)"

def create_attributes():
    """
    Insert docstring here
    """
    oproperty = Property.objects.get(prefix="ALL")
    oattribute = Attribute()
    oattribute.value = oproperty.name
    oattribute.property_att = oproperty
    oattribute.description = ""
    oattribute.save()
    print "Attribute (add ALL - ALL SYSTEMS)"

    """
    oproperty = Property.objects.get(prefix="CTX")
    oattribute = Attribute()
    oattribute.value = "RYS.AYTOZAR"
    oattribute.property_att = oproperty
    oattribute.description = ""
    oattribute.save()
    print "Attribute (add CTX - RYS.AYTOZAR)"

    oproperty = Property.objects.get(prefix="CTX")
    oattribute = Attribute()
    oattribute.value = "IYD.AYTOZAR"
    oattribute.property_att = oproperty
    oattribute.description = ""
    oattribute.save()
    print "Attribute (add CTX - IYD.AYTOZAR)"

    oproperty = Property.objects.get(prefix="CTX")
    oattribute = Attribute()
    oattribute.value = "MODERNIZACION.AYTOZAR"
    oattribute.property_att = oproperty
    oattribute.description = ""
    oattribute.save()
    print "Attribute (add CTX - MODERNIZACION.AYTOZAR)"

    oproperty = Property.objects.get(prefix="CTX")
    oattribute = Attribute()
    oattribute.value = "AYTOZAR"
    oattribute.property_att = oproperty
    oattribute.description = ""
    oattribute.save()
    print "Attribute (add CTX - AYTOZAR)"
    """

def create_schedules():
    """
    Insert docstring here
    """
    oschedule = Schedule()
    oschedule.name = "STANDARD"
    oschedule.description = "Default schedule. By context."
    oschedule.save()
    print "Schedule (add STANDARD)"

    oschedule = Schedule()
    oschedule.name = "SLOW"
    oschedule.description = "By context, slowly."
    oschedule.save()
    print "Schedule (add SLOW)"

def create_schedules_delays():
    """
    Insert docstring here
    """

    """
    oscheduledelay = ScheduleDelay()
    oscheduledelay.delay = 3
    oscheduledelay.schedule = Schedule.objects.get(name="STANDARD")
    oscheduledelay.save()
    oscheduledelay.attributes.add(Attribute.objects.get(value="RYS.AYTOZAR").id)
    oscheduledelay.save()
    print "ScheduleDelay (add 3 STANDARD)"

    oscheduledelay = ScheduleDelay()
    oscheduledelay.delay = 6
    oscheduledelay.schedule = Schedule.objects.get(name="STANDARD")
    oscheduledelay.save()
    oscheduledelay.attributes.add(Attribute.objects.get(value="IYD.AYTOZAR").id,)
    oscheduledelay.save()
    print "ScheduleDelay (add 6 STANDARD)"

    oscheduledelay = ScheduleDelay()
    oscheduledelay.delay = 9
    oscheduledelay.schedule = Schedule.objects.get(name="STANDARD")
    oscheduledelay.save()
    oscheduledelay.attributes.add(Attribute.objects.get(value="AYTOZAR").id,)
    oscheduledelay.save()
    print "ScheduleDelay (add 9 STANDARD)"
    """

    oscheduledelay = ScheduleDelay()
    oscheduledelay.delay = 12
    oscheduledelay.schedule = Schedule.objects.get(name="STANDARD")
    oscheduledelay.save()
    oscheduledelay.attributes.add(Attribute.objects.get(value="ALL SYSTEMS").id,)
    oscheduledelay.save()
    print "ScheduleDelay (add 12 STANDARD)"

def create_devices():
    """
    Insert docstring here
    """
    odevicemanufacturer = DeviceManufacturer()
    odevicemanufacturer.name = "EPSON"
    odevicemanufacturer.save()
    print "DeviceManufacturer (add EPSON)"

    odevicemanufacturer = DeviceManufacturer()
    odevicemanufacturer.name = "FUJITSU"
    odevicemanufacturer.save()
    print "DeviceManufacturer (add FUJITSU)"

    odevicemanufacturer = DeviceManufacturer()
    odevicemanufacturer.name = "HP"
    odevicemanufacturer.save()
    print "DeviceManufacturer (add HP)"

    odevicemanufacturer = DeviceManufacturer()
    odevicemanufacturer.name = "CANON"
    odevicemanufacturer.save()
    print "DeviceManufacturer (add CANON)"

    odevicemanufacturer = DeviceManufacturer()
    odevicemanufacturer.name = "OTHERS"
    odevicemanufacturer.save()
    print "DeviceManufacturer (add OTHERS)"

    odevicetype = DeviceType()
    odevicetype.name = "SCANNER"
    odevicetype.save()
    print "DeviceType (add SCANNER)"

    odeviceconnection = DeviceConnection()
    odeviceconnection.name = "USB"
    odeviceconnection.fields = ""
    odeviceconnection.devicetype = odevicetype
    odeviceconnection.install = "echo HERE-INSTALL-CODE-SCANNER-USB"
    odeviceconnection.remove = "echo HERE-REMOVE- CODE-SCANNER-USB"
    odeviceconnection.save()
    print "DeviceConnection (add USB SCANNER)"

    odeviceconnection = DeviceConnection()
    odeviceconnection.name = "TCP"
    odeviceconnection.fields = "IP"
    odeviceconnection.devicetype = odevicetype
    odeviceconnection.install = "echo HERE-INSTALL-CODE-SCANNER-TCP"
    odeviceconnection.remove = "echo HERE-REMOVE- CODE-SCANNER-TCP"
    odeviceconnection.save()
    print "DeviceConnection (add TCP SCANNER)"

    odevicetype = DeviceType()
    odevicetype.name = "PRINTER"
    odevicetype.save()
    print "DeviceType (add PRINTER)"

    odeviceconnection = DeviceConnection()
    odeviceconnection.name = "USB"
    odeviceconnection.uri = "parallel:/dev/usb/lp0"
    odeviceconnection.fields = ""
    odeviceconnection.devicetype = odevicetype
    odeviceconnection.install = "/usr/sbin/lpadmin -p $_NAME -P $_FILE -v parallel:/dev/usb/lp0 -E"
    odeviceconnection.remove = "/usr/sbin/lpadmin -x $_NAME"
    odeviceconnection.save()
    print "DeviceConnection (add USB PRINTER)"

    #odeviceconnection = DeviceConnection()
    #odeviceconnection.name = "LPT (tipix)"
    #odeviceconnection.fields = ""
    #odeviceconnection.devicetype = odevicetype
    #odeviceconnection.install = "/usr/sbin/lpadmin -p tipix -v parallel:/dev/lp0 -E"
    #odeviceconnection.remove = "/usr/sbin/lpadmin -x $_NAME"
    #odeviceconnection.save()
    #print "DeviceConnection (add LPT (tipix) PRINTER)"

    odeviceconnection = DeviceConnection()
    odeviceconnection.name = "LPT"
    odeviceconnection.uri = "parallel:/dev/lp0"
    odeviceconnection.fields = ""
    odeviceconnection.devicetype = odevicetype
    odeviceconnection.install = "/usr/sbin/lpadmin -p $_NAME -P $_FILE -v parallel:/dev/lp0 -E"
    odeviceconnection.remove = "/usr/sbin/lpadmin -x $_NAME"
    odeviceconnection.save()
    print "DeviceConnection (add LPT PRINTER)"

    odeviceconnection = DeviceConnection()
    odeviceconnection.name = "TCP"
    odeviceconnection.uri = "socket://{IP}:9100"
    odeviceconnection.fields = "IP LOCATION"
    odeviceconnection.devicetype = odevicetype
    odeviceconnection.install = "/usr/sbin/lpadmin -p $_NAME -P $_FILE -v socket://$_IP:9100 -E -L \"$_LOCATION\""
    odeviceconnection.remove = "/usr/sbin/lpadmin -x $_NAME"
    odeviceconnection.save()
    print "DeviceConnection (add TCP PRINTER)"

    odeviceconnection = DeviceConnection()
    odeviceconnection.name = "TCP:9101"
    odeviceconnection.uri = "socket://{IP}:9101"
    odeviceconnection.fields = "IP"
    odeviceconnection.devicetype = odevicetype
    odeviceconnection.install = "/usr/sbin/lpadmin -p $_NAME -P $_FILE -v socket://$_IP:9101 -E"
    odeviceconnection.remove = "/usr/sbin/lpadmin -x $_NAME"
    odeviceconnection.save()
    print "DeviceConnection (add TCP:9101 PRINTER)"

    odeviceconnection = DeviceConnection()
    odeviceconnection.name = "TCP:9102"
    odeviceconnection.uri = "socket://{IP}:9102"
    odeviceconnection.fields = "IP"
    odeviceconnection.devicetype = odevicetype
    odeviceconnection.install = "/usr/sbin/lpadmin -p $_NAME -P $_FILE -v socket://$_IP:9102 -E"
    odeviceconnection.remove = "/usr/sbin/lpadmin -x $_NAME"
    odeviceconnection.save()
    print "DeviceConnection (add TCP:9102 PRINTER)"

    odevicemodel = DeviceModel()
    odevicemodel.name = "EPL-N2550"
    odevicemodel.manufacturer = DeviceManufacturer.objects.get(name="EPSON")
    odevicemodel.devicetype = odevicetype
    odevicemodel.filename = "/usr/share/cups/model/Epson/EPL-N2500PS-Postscript.ppd.gz"
    odevicemodel.preinstall = "# HERE-PREINSTALL-MODEL-"+odevicemodel.name
    odevicemodel.postinstall = "# HERE-POSTINSTALL-MODEL-"+odevicemodel.name
    odevicemodel.preremove = "# HERE-PREREMOVE-MODEL-"+odevicemodel.name
    odevicemodel.postremove = "# HERE-POSTREMOVE-MODEL-"+odevicemodel.name
    odevicemodel.save()
    odevicemodel.connections.add(DeviceConnection.objects.get(name="USB", devicetype=2).id)
    odevicemodel.connections.add(DeviceConnection.objects.get(name="TCP", devicetype=2).id)
    odevicemodel.save()
    print "DeviceModel (add EPL-N2550)"

    odevicemodel = DeviceModel()
    odevicemodel.name = "EPL-5400"
    odevicemodel.manufacturer = DeviceManufacturer.objects.get(name="EPSON")
    odevicemodel.devicetype = odevicetype
    odevicemodel.filename = "/usr/share/cups/model/Epson/EPL-N2500PS-Postscript.ppd.gz"
    odevicemodel.preinstall = "# HERE-PREINSTALL-MODEL-"+odevicemodel.name
    odevicemodel.postinstall = "# HERE-POSTINSTALL-MODEL-"+odevicemodel.name
    odevicemodel.preremove = "# HERE-PREREMOVE-MODEL-"+odevicemodel.name
    odevicemodel.postremove = "# HERE-POSTREMOVE-MODEL-"+odevicemodel.name
    odevicemodel.save()
    odevicemodel.connections.add(DeviceConnection.objects.get(name="LPT", devicetype=2).id)
    odevicemodel.save()
    print "DeviceModel (add EPL-5400)"

    odevicemodel = DeviceModel()
    odevicemodel.name = "IRC-5000"
    odevicemodel.manufacturer = DeviceManufacturer.objects.get(name="CANON")
    odevicemodel.devicetype = odevicetype
    odevicemodel.filename = "/usr/share/cups/model/Epson/EPL-N2500PS-Postscript.ppd.gz"
    odevicemodel.preinstall = "# HERE-PREINSTALL-MODEL-"+odevicemodel.name
    odevicemodel.postinstall = "# HERE-POSTINSTALL-MODEL-"+odevicemodel.name
    odevicemodel.preremove = "# HERE-PREREMOVE-MODEL-"+odevicemodel.name
    odevicemodel.postremove = "# HERE-POSTREMOVE-MODEL-"+odevicemodel.name
    odevicemodel.save()
    odevicemodel.connections.add(DeviceConnection.objects.get(name="TCP", devicetype=2).id)
    odevicemodel.save()
    print "DeviceModel (add IRC-5000)"

    odevicemodel = DeviceModel()
    odevicemodel.name = "tipix"
    odevicemodel.manufacturer = DeviceManufacturer.objects.get(name="OTHERS")
    odevicemodel.devicetype = odevicetype
    odevicemodel.filename = ""
    odevicemodel.preinstall = "# HERE-PREINSTALL-MODEL-"+odevicemodel.name
    odevicemodel.postinstall = "# HERE-POSTINSTALL-MODEL-"+odevicemodel.name
    odevicemodel.preremove = "# HERE-PREREMOVE-MODEL-"+odevicemodel.name
    odevicemodel.postremove = "# HERE-POSTREMOVE-MODEL-"+odevicemodel.name
    odevicemodel.save()
    odevicemodel.connections.add(DeviceConnection.objects.get(name="LPT", devicetype=2).id)
    odevicemodel.save()
    print "DeviceModel (tipix)"

def create_queries():
    """
    Insert docstring here
    """
    oquery = Query()
    oquery.name = "QUERIES"
    oquery.description = "LIST OF QUERIES"
    oquery.code = \
"""if parameters['id'] == '':
    query = Query.objects.all()
else:
    query = Query.objects.filter(id=parameters['id'])
    fields = ('id', 'name', 'description', 'code', 'parameters')
"""
    oquery.parameters = \
"""def form_params():
    from migasfree.server.forms import ParametersForm
    class myForm(ParametersForm):
        id = forms.CharField()
    return myForm
"""
    oquery.save()
    print "Query (add QUERIES)"

    oquery = Query()
    oquery.name = "PACKAGES/SETS"
    oquery.description = "LIST OF PACKAGES/SETS"
    oquery.code = \
"""query = Package.objects.filter(name__contains=parameters['name'])
fields = ('id', 'link()', 'store.name')
titles = ('id', 'name', 'store')
"""
    oquery.parameters = \
"""def form_params():
    from migasfree.server.forms import ParametersForm
    class myForm(ParametersForm):
        name = forms.CharField()
    return myForm
"""
    oquery.save()
    print "Query (add PACKAGES/SETS)"

    oquery = Query()
    oquery.name = "COMPUTERS BY ATTRIBUTES"
    oquery.description = "LIST THE COMPUTERS THAT HAVE A DETERMINATE ATTRIBUTE"
    oquery.code = \
"""query = Login.objects.all()
if parameters['value'] != '':
    query = query.filter(attributes__property_att__id = parameters['property_att'], attributes__value__contains = parameters['value'])
    fields = ('computer.link()', 'user.link()', 'date')
    titles = ('computer', 'user', 'date of login')
"""
    oquery.parameters = \
"""def form_params():
    from migasfree.server.forms import ParametersForm
    class myForm(ParametersForm):
        property_att = forms.ModelChoiceField(Property.objects.all())
        value = forms.CharField()
    return myForm
"""
    oquery.save()
    print "Query (add COMPUTERS BY ATTRIBUTES)"

    oquery = Query()
    oquery.name = "COMPUTERS WITH THE PACKAGE..."
    oquery.description = "LIST THE COMPUTERS WITH THE PACKAGE ESPECIFIQUED"
    oquery.code = \
"""query = Computer.objects.filter(software__contains=parameters['package'])
fields = ('link()', 'software')
titles = ('link()', 'diff with master')
"""
    oquery.parameters = \
"""def form_params():
    from migasfree.server.forms import ParametersForm
    class myForm(ParametersForm):
        package = forms.CharField()
    return myForm
"""
    oquery.save()
    print "Query (add COMPUTERS WITH THE PACKAGE...)"

    oquery = Query()
    oquery.name = "PACKAGE/SET ORPHAN"
    oquery.description = "PACKAGES/SET THAT NOT HAVE BEEN ASIGNED TO A REPOSITORY"
    oquery.code = \
"""query = Package.objects.version(0).filter(Q(repository__id__exact=None))
fields = ('version.name', 'store.name', 'link()')
titles = ('version', 'store', 'package/set')
"""
    oquery.parameters = ""
    oquery.save()
    print "Query (add PACKAGE/SET ORPHAN)"

    oquery = Query()
    oquery.name = "REPOSITORIES WITH A PACKAGE/SET"
    oquery.description = "LIST THE REPOSITORIES THAT HAVE ASIGNNED A DETERMINATE PACKAGE/SET"
    oquery.code = \
"""from migasfree.server.models import Repository
query = Repository.objects.filter(version=version).filter(Q(packages__name__contains=parameters['package']))
query = query.distinct()
fields = ('id', 'link()', 'packages_link()')
titles = ('id', 'Repository', 'Packages')
"""
    oquery.parameters = \
"""def form_params():
    from migasfree.server.forms import ParametersForm
    class myForm(ParametersForm):
        package = forms.CharField()
    return myForm
"""
    oquery.save()
    print "Query (add REPOSITORIES WITH A PACKAGE/SET)"

    oquery = Query()
    oquery.name = "LAST LOGIN"
    oquery.description = "LIST OF LAST LOGIN FROM COMPUTERS"
    oquery.code = \
"""query = Login.objects.all()
fields = ('computer.link()', 'computer.login_link()', 'computer.last_login().user.link()')
titles = ('computer', 'last login', 'user')
"""
    oquery.parameters = ""
    oquery.save()
    print "Query (add LAST LOGIN)"

    oquery = Query()
    oquery.name = "COMPUTER DEVICES"
    oquery.description = ""
    oquery.code = \
"""query = Computer.objects.all()
if parameters['model'] != '':
    query = query.filter(devices__model__id=parameters['model'])
    query = query.filter(name__contains=parameters['computer'])
    query = query.order_by('name')
    fields = ('link()', 'devices_link()', 'login_link()')
    titles = ('computer', 'devices', 'last login')
"""
    oquery.parameters = \
"""def form_params():
    from migasfree.server.forms import ParametersForm
    class myForm(ParametersForm):
        model = forms.ModelChoiceField(DeviceModel.objects.all())
        computer = forms.CharField()
    return myForm
"""
    oquery.save()
    print "Query (add COMPUTER DEVICES)"

    oquery = Query()
    oquery.name = "DEVICE COMPUTERS"
    oquery.description = ""
    oquery.code = \
"""query = Device.objects.all()
if parameters['model'] != '':
  query = query.filter(Q(model__id=parameters['model']))
  query = query.filter(Q(computer__name__contains=parameters['computer']))
  query = query.order_by('name').distinct()
  fields = ('link()', 'model.link()', 'computers_link()')
  titles = ('device', 'model', 'computers')
"""
    oquery.parameters = \
"""def form_params():
    from migasfree.server.forms import ParametersForm
    class myForm(ParametersForm):
        model = forms.ModelChoiceField(DeviceModel.objects.all())
        computer = forms.CharField()
    return myForm
"""
    oquery.save()
    print "Query (add DEVICE COMPUTERS)"

def create_users_groups():
    """
    Insert docstring here
    """
    ogroupread = Group()
    ogroupread.name = "Read"
    ogroupread.save()
    ogroupread.permissions.add(Permission.objects.get(codename="change_computer").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_device").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_user", content_type__app_label="server").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_login").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_attribute").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_error").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_fault").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_deviceconnection").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_devicemanufacturer").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_devicemodel").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_devicetype").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_schedule").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_scheduledelay").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_autocheckerror").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_faultdef").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_property").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_checking").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_version").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_pms").id)
    #ogroupread.permissions.add(Permission.objects.get(codename="change_variable").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_query").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_package").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_repository").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_store").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_message", content_type__app_label="server").id)
    ogroupread.permissions.add(Permission.objects.get(codename="change_update").id)
    ogroupread.save()

    oGroupRepo = Group()
    oGroupRepo.name = "Change Software Configuration"
    oGroupRepo.save()
    oGroupRepo.permissions.add(Permission.objects.get(codename="add_repository").id)
    oGroupRepo.permissions.add(Permission.objects.get(codename="change_repository").id)
    oGroupRepo.permissions.add(Permission.objects.get(codename="can_save_repository").id)
    oGroupRepo.permissions.add(Permission.objects.get(codename="delete_repository").id)
    oGroupRepo.permissions.add(Permission.objects.get(codename="add_schedule").id)
    oGroupRepo.permissions.add(Permission.objects.get(codename="change_schedule").id)
    oGroupRepo.permissions.add(Permission.objects.get(codename="can_save_schedule").id)
    oGroupRepo.permissions.add(Permission.objects.get(codename="delete_schedule").id)
    oGroupRepo.permissions.add(Permission.objects.get(codename="add_scheduledelay").id)
    oGroupRepo.permissions.add(Permission.objects.get(codename="change_scheduledelay").id)
    oGroupRepo.permissions.add(Permission.objects.get(codename="can_save_scheduledelay").id)
    oGroupRepo.permissions.add(Permission.objects.get(codename="delete_scheduledelay").id)
    oGroupRepo.save()

    ogrouppackager = Group()
    ogrouppackager.name = "Packager"
    ogrouppackager.save()
    ogrouppackager.permissions.add(Permission.objects.get(codename="add_package").id)
    ogrouppackager.permissions.add(Permission.objects.get(codename="change_package").id)
    ogrouppackager.permissions.add(Permission.objects.get(codename="can_save_package").id)
    ogrouppackager.permissions.add(Permission.objects.get(codename="delete_package").id)
    ogrouppackager.permissions.add(Permission.objects.get(codename="add_store").id)
    ogrouppackager.permissions.add(Permission.objects.get(codename="change_store").id)
    ogrouppackager.permissions.add(Permission.objects.get(codename="can_save_store").id)
    ogrouppackager.permissions.add(Permission.objects.get(codename="delete_store").id)
    ogrouppackager.save()

    ogroupcheck = Group()
    ogroupcheck.name = "Check"
    ogroupcheck.save()
    ogroupcheck.permissions.add(Permission.objects.get(codename="add_autocheckerror").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="change_autocheckerror").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="can_save_autocheckerror").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="delete_autocheckerror").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="add_error").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="change_error").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="can_save_error").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="delete_error").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="add_fault").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="change_fault").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="can_save_fault").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="delete_fault").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="add_message", content_type__app_label="server").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="change_message", content_type__app_label="server").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="can_save_message", content_type__app_label="server").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="delete_message", content_type__app_label="server").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="add_update").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="change_update").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="can_save_update").id)
    ogroupcheck.permissions.add(Permission.objects.get(codename="delete_update").id)
    ogroupcheck.save()

    ogroupdev = Group()
    ogroupdev.name = "Devices"
    ogroupdev.save()
    ogroupdev.permissions.add(Permission.objects.get(codename="add_deviceconnection").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="change_deviceconnection").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="can_save_deviceconnection").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="delete_deviceconnection").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="add_devicemanufacturer").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="change_devicemanufacturer").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="can_save_devicemanufacturer").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="delete_devicemanufacturer").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="add_devicemodel").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="change_devicemodel").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="can_save_devicemodel").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="delete_devicemodel").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="add_devicetype").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="change_devicetype").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="can_save_devicetype").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="delete_devicetype").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="add_devicefile").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="change_devicefile").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="can_save_devicefile").id)
    ogroupdev.permissions.add(Permission.objects.get(codename="delete_devicefile").id)
    ogroupdev.save()

    ogroupquery = Group()
    ogroupquery.name = "Query"
    ogroupquery.save()
    ogroupquery.permissions.add(Permission.objects.get(codename="add_query").id)
    ogroupquery.permissions.add(Permission.objects.get(codename="change_query").id)
    ogroupquery.permissions.add(Permission.objects.get(codename="can_save_query").id)
    ogroupquery.permissions.add(Permission.objects.get(codename="delete_query").id)
    ogroupquery.save()

    ogroupsys = Group()
    ogroupsys.name = "System"
    ogroupsys.save()
    ogroupsys.permissions.add(Permission.objects.get(codename="add_checking").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="change_checking").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="can_save_checking").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="delete_checking").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="add_faultdef").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="change_faultdef").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="can_save_faultdef").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="delete_faultdef").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="add_property").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="change_property").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="can_save_property").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="delete_property").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="add_pms").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="change_pms").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="can_save_pms").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="delete_pms").id)
    #ogroupsys.permissions.add(Permission.objects.get(codename="add_variable").id)
    #ogroupsys.permissions.add(Permission.objects.get(codename="change_variable").id)
    #ogroupsys.permissions.add(Permission.objects.get(codename="can_save_variable").id)
    #ogroupsys.permissions.add(Permission.objects.get(codename="delete_variable").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="add_version").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="change_version").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="can_save_version").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="delete_version").id)

    ogroupsys.permissions.add(Permission.objects.get(codename="add_message", content_type__app_label="server").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="change_message", content_type__app_label="server").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="can_save_message", content_type__app_label="server").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="delete_message", content_type__app_label="server").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="add_update").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="change_update").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="can_save_update").id)
    ogroupsys.permissions.add(Permission.objects.get(codename="delete_update").id)
    ogroupsys.save()

def create_users():
    """
    Insert docstring here
    """
    ogroupread = Group.objects.get(name="Read")
    ogroupsys = Group.objects.get(name="System")
    ogroupdev = Group.objects.get(name="Devices")
    ogroupquery = Group.objects.get(name="Query")
    ogrouppackager = Group.objects.get(name="Packager")
    oGroupRepo = Group.objects.get(name="Change Software Configuration")
    ogroupcheck = Group.objects.get(name="Check")

    ouser = UserProfile()
    ouser.username = "admin"
    ouser.is_staff = True
    ouser.is_active = True
    ouser.is_superuser = True
    ouser.set_password("admin")
    ouser.save()

    ouser = UserProfile()
    ouser.username = "system"
    ouser.is_staff = True
    ouser.is_active = True
    ouser.is_superuser = False
    ouser.set_password("system")
    ouser.save()
    ouser.groups.add(ogroupread.id)
    ouser.groups.add(ogroupsys.id)
    ouser.save()

    ouser = UserProfile()
    ouser.username = "device"
    ouser.is_staff = True
    ouser.is_active = True
    ouser.is_superuser = False
    ouser.set_password("device")
    ouser.save()
    ouser.groups.add(ogroupread.id)
    ouser.groups.add(ogroupdev.id)
    ouser.save()

    ouser = UserProfile()
    ouser.username = "query"
    ouser.is_staff = True
    ouser.is_active = True
    ouser.is_superuser = False
    ouser.set_password("query")
    ouser.save()
    ouser.groups.add(ogroupread.id)
    ouser.groups.add(ogroupquery.id)
    ouser.save()

    ouser = UserProfile()
    ouser.username = "packager"
    ouser.is_staff = True
    ouser.is_active = True
    ouser.is_superuser = False
    ouser.set_password("packager")
    ouser.save()
    ouser.groups.add(ogroupread.id)
    ouser.groups.add(ogrouppackager.id)
    ouser.save()

    ouser = UserProfile()
    ouser.username = "repo"
    ouser.is_staff = True
    ouser.is_active = True
    ouser.is_superuser = False
    ouser.set_password("repo")
    ouser.save()
    ouser.groups.add(ogroupread.id)
    ouser.groups.add(oGroupRepo.id)
    ouser.save()

    ouser = UserProfile()
    ouser.username = "check"
    ouser.is_staff = True
    ouser.is_active = True
    ouser.is_superuser = False
    ouser.set_password("check")
    ouser.save()
    ouser.groups.add(ogroupread.id)
    ouser.groups.add(ogroupcheck.id)
    ouser.save()

    ouser = UserProfile()
    ouser.username = "read"
    ouser.is_staff = True
    ouser.is_active = True
    ouser.is_superuser = False
    ouser.set_password("read")
    ouser.save()
    ouser.groups.add(ogroupread.id)
    ouser.save()

def main():
    """
    LOAD DATA TO migasfree database
    """
    create_pms()
    create_checkings()
    create_properties()
    create_faultdefs()
    create_attributes()
    create_schedules()
    create_schedules_delays()
    create_devices()
    create_queries()
    create_users_groups()
    create_users()

if __name__ == '__main__':
    main()
