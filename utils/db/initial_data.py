
from django.utils.translation import ugettext as _
from migasfree.system.models import *
from migasfree.system.logic import CreateRepositories
from datetime import datetime
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
import os

#LOAD DATA TO BD migasfree



#VARIABLES
oVariable=Variable()
oVariable.name="MEDIA"
#oVariable.value="/srv/www/htdocs/media/"
oVariable.value="/var/www/htdocs/media/"
oVariable.save()

oVariable=Variable()
oVariable.name="PATH_REPO"
#oVariable.value="/srv/www/htdocs/repo/"
oVariable.value="/var/www/htdocs/repo/"
oVariable.save()

oVariable=Variable()
oVariable.name="USER_WEB_SERVER"
#oVariable.value="wwwrun"
oVariable.value="www-data"
oVariable.save()

oVariable=Variable()
oVariable.name="ORGANIZATION"
oVariable.value="My Organization"
oVariable.save()


oVariable=Variable()
oVariable.name="SECONDS_MESSAGE_ALERT"
oVariable.value="1800"
oVariable.save()


#PACKAGE MANAGEMENT SYSTEM
oPms=Pms()
oPms.name="yum"
cad="_DIRECTORY=%PATH%/%REPONAME%\n"
cad=cad+"rm -rf $_DIRECTORY/repodata\n"
cad=cad+"rm -rf $_DIRECTORY/checksum\n"
cad=cad+"createrepo -c checksum $_DIRECTORY\n"
oPms.createrepo=cad
cad="[%REPO%]\n"
cad=cad+"name=%REPO%\n"
cad=cad+"baseurl=http://$MIGASFREE_SERVER/repo/%VERSION%/REPOSITORIES/%REPO%\n"
cad=cad+"gpgcheck=0\n"
cad=cad+"enabled=1\n"
cad=cad+"http_caching=none\n"
cad=cad+"metadata_expire=1\n"
oPms.repository=cad
cad="echo ****INFO****\n"
cad=cad+"rpm -qp --info $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****REQUIRES****\n"
cad=cad+"rpm -qp --requires $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****PROVIDES****\n"
cad=cad+"rpm -qp --provides $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****OBSOLETES****\n"
cad=cad+"rpm -qp --obsoletes $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****SCRIPTS****\n"
cad=cad+"rpm -qp --scripts $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****CHANGELOG****\n"
cad=cad+"rpm -qp --changelog $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****FILES****\n"
cad=cad+"rpm -qp --list $PACKAGE\n"
cad=cad+"echo\n"
oPms.info=cad
oPms.save()
print "Package Management System (added yum)"

oPms=Pms()
oPms.name="zypper"
cad="_DIRECTORY=%PATH%/%REPONAME%\n"
cad=cad+"rm -rf $_DIRECTORY/repodata\n"
cad=cad+"rm -rf $_DIRECTORY/checksum\n"
cad=cad+"createrepo -c checksum $_DIRECTORY\n"
oPms.createrepo=cad
cad="[%REPO%]\n"
cad=cad+"name=%REPO%\n"
cad=cad+"baseurl=http://$MIGASFREE_SERVER/repo/%VERSION%/REPOSITORIES/%REPO%\n"
cad=cad+"gpgcheck=0\n"
cad=cad+"enabled=1\n"
cad=cad+"http_caching=none\n"
cad=cad+"metadata_expire=1\n"
oPms.repository=cad
cad="echo ****INFO****\n"
cad=cad+"rpm -qp --info $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****REQUIRES****\n"
cad=cad+"rpm -qp --requires $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****PROVIDES****\n"
cad=cad+"rpm -qp --provides $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****OBSOLETES****\n"
cad=cad+"rpm -qp --obsoletes $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****SCRIPTS****\n"
cad=cad+"rpm -qp --scripts $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****CHANGELOG****\n"
cad=cad+"rpm -qp --changelog $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****FILES****\n"
cad=cad+"rpm -qp --list $PACKAGE\n"
cad=cad+"echo\n"
oPms.info=cad
oPms.save()
print "Package Management System (added zypper)"

oPms=Pms()
oPms.name="apt"
oPms.slug="REPOSITORIES/dists"
cad="cd %PATH%\n"
cad=cad+"mkdir -p %REPONAME%/PKGS/binary-i386/\n"
cad=cad+"mkdir -p %REPONAME%/PKGS/sources/\n"
cad=cad+"cd ..\n"
cad=cad+"dpkg-scanpackages dists/%REPONAME%/PKGS /dev/null | gzip -9c > dists/%REPONAME%/PKGS/binary-i386/Packages.gz\n"
cad=cad+"dpkg-scansources dists/%REPONAME%/PKGS /dev/null | gzip -9c > dists/%REPONAME%/PKGS/sources/Sources.gz\n"
oPms.createrepo=cad
cad="deb http://$MIGASFREE_SERVER/repo/%VERSION%/REPOSITORIES %REPO% PKGS\n"
oPms.repository=cad
cad="echo ****INFO****\n"
cad=cad+"dpkg -I $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****REQUIRES****\n"
cad=cad+"dpkg-deb --showformat='${Depends}\n' --show $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****PROVIDES****\n"
cad=cad+"dpkg-deb --showformat='${Provides}\n' --show $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****OBSOLETES****\n"
cad=cad+"dpkg-deb --showformat='${Replaces}\n' --show $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****SCRIPTS****\n"
cad=cad+"dpkg-deb --showformat='${Source}\n' --show $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****CHANGELOG****\n"
cad=cad+"#rpm -qp --changelog $PACKAGE\n"
cad=cad+"echo\n"
cad=cad+"echo\n"
cad=cad+"echo ****FILES****\n"
cad=cad+"dpkg-deb -c $PACKAGE | awk '{print $6}'\n"
oPms.info=cad
oPms.save()
print "Package Management System (add apt)"
 

#VERSIONS
oPms=Pms.objects.get(name="yum")
oVersion=Version()
oVersion.name="FEDORA"
oVersion.pms=oPms
oVersion.save()
print "Version (add FEDORA)"

oPms=Pms.objects.get(name="zypper")
oVersion=Version()
oVersion.name="OPENSUSE"
oVersion.pms=oPms
oVersion.save()
print "Version (add OPENSUSE)"

oPms=Pms.objects.get(name="apt")
oVersion=Version()
oVersion.name="UBUNTU"
oVersion.pms=oPms
oVersion.save()
print "Version (add UBUNTU)"


#CHECKING
oChecking=Checking()
oChecking.name=_("Errors to check")
oChecking.description="Errors not marked as checked. You must mark the error as checked when the error is solutioned."
oChecking.code="result=Error.objects.filter(checked__exact=0).count()\nurl='/migasfree/admin/system/error/?checked__exact=0'\nicon='error.png'\nmessage='Errors to check'"
oChecking.save()

oChecking=Checking()
oChecking.name=_("Faults to check")
oChecking.description="Faults not marked as checked. You must mark the fault as checked when the fault is solutioned"
oChecking.code="result=Fault.objects.filter(checked__exact=0).count()\nurl='/migasfree/admin/system/fault/?checked__exact=0'\nicon='fault.png'\nmessage='Faults to check'"
oChecking.save()

oChecking=Checking()
oChecking.name=_("Package/Set orphan")
oChecking.description="Packages that not have been asigned to a Repository."
oChecking.code="result=Package.objects.version(0).filter(Q(repository__id__exact=None)).count()\nurl='/migasfree/query/?id=5'\nicon='information.png'\nmessage='Package/Set orphan'"
oChecking.save()

oChecking=Checking()
oChecking.name=_("Repositories files creation")
oChecking.description="Check if the current user version have to create the files of repositories (only will be created when in a Repository you change the packackes)"
oChecking.code="from migasfree.system.logic import compare_values\nresult=0\nds=Repository.objects.all()\nfor d in ds:\n    if not compare_values(d.packages.values('id'),d.createpackages.values('id')):\n        result=result+1\nurl='/migasfree/createrepositories'\nicon='repository.png'\nmessage='Repositories files creation'"
oChecking.save()

oChecking=Checking()
oChecking.name=_("Computer updating now")
oChecking.description="Check how many computers are being updated at this time"
oChecking.code="from datetime import datetime\nfrom datetime import timedelta\nSECONDS_MESSAGE_ALERT=int(getVariable('SECONDS_MESSAGE_ALERT'))\noMessages=Message.objects.all()\nresult=oMessages.count()\nurl='/migasfree/queryMessage'\nmessage='Computer updating now'\nt=datetime.now()-timedelta(0,SECONDS_MESSAGE_ALERT)\nn= Message.objects.filter(date__lt = t).count()\nif n > 0:\n    icon='computer_alert.png'\nelse:\n    icon='computer.png'"
oChecking.save()




#PROPERTIES DEFINITION
oProperty=Property()
oProperty.prefix="ALL"
cad="    echo \"ALL SYSTEMS\"\n"
oProperty.function=cad
oProperty.name="ALL SYSTEMS"
oProperty.save()
print "Property (add LDAP GROUP)"




oProperty=Property()
oProperty.prefix="IP"
oProperty.function="  getip | awk 'BEGIN {FS=\"/\"}; {print $1}'"
oProperty.name="IP DIRECTION"
oProperty.save()
print "Property (add IP DIRECTION)"

oProperty=Property()
oProperty.prefix="NET"
oProperty.function="  getip"
oProperty.before_insert="#Convert the IP direction in the net direction, thanks to IPy module\nfrom IPy import IP\ndata=str(IP(data,make_net=True))"
oProperty.name="NET"
oProperty.save()
print "Property (add NET)"



oProperty=Property()
oProperty.prefix="GRP"
cad="    echo \"GRP-AU,GRP-Administradores,GRP-Impresoras\"\n"
oProperty.function=cad
oProperty.name="LDAP GROUP"
oProperty.kind="-"
oProperty.save()
print "Property (add LDAP GROUP)"

oProperty=Property()
oProperty.prefix="CTX"
cad="  echo RYS.AYTOZAR\n"
oProperty.function=cad
oProperty.name="LDAP CONTEXT"
oProperty.kind="R"
oProperty.save()
print "Property (add LDAP CONTEXT)"


oProperty=Property()
oProperty.prefix="HST"
cad="    echo $HOSTNAME\n"
oProperty.function=cad
oProperty.name="MACHINE NAME"
oProperty.save()
print "Property (add MACHINE NAME)"


oProperty=Property()
oProperty.prefix="PCI"
cad="  local r=\"\"\n"
cad=cad+"  if [ `lspci -n |sed -n 1p|awk '{print $2}'` = 'Class' ]; then\n"
cad=cad+"    dev=`lspci -n |awk '{print $4}'`\n"
cad=cad+"  else\n"
cad=cad+"    dev=`lspci -n |awk '{print $3}'`\n"
cad=cad+"  fi\n"
cad=cad+"  for l in $dev; do\n"
cad=cad+"    n=`lspci -d $l|awk '{for (i = 2; i <=NF;++i) print $i}'|tr \"\\n\" \" \" |sed 's/,//g'`\n"
cad=cad+"    r=\"$r$l~$n,\"\n"
cad=cad+"  done\n"
cad=cad+"  echo $r\n"
oProperty.function=cad
oProperty.name="DEVICE PCI"
oProperty.kind="-"
oProperty.save()
print "Property (add DEVICE PCI)"




oProperty=Property()
oProperty.prefix="USR"
cad="  echo $_USER_GRAPHIC\n"
oProperty.function=cad
oProperty.name="USER"
oProperty.save()
print "Property (add USER)"


#FAULTS
oFaultDef=FaultDef()
oFaultDef.name="LOW SYSTEM PARTITION SPACE"
oFaultDef.description="add a fault when the space in partition of system is low"
cad="local let limite=15 #PORCENTAJE DE USO EN PARTICION /\n"
cad=cad+"local DEVICE=`mount |grep \" on / \"|awk '{print $1}'`\n"
cad=cad+"local let usado=`df -hl| grep $DEVICE| awk '{print $5}'|awk 'BEGIN {FS=\"%\";} {print $1}'`\n"
cad=cad+"if [ $usado -gt $limite ] ; then\n"
cad=cad+"  echo \"El espacio usado en la particion de sistema $DEVICE es de un $usado%, superando el limite establecido en $limite%\"\n"
cad=cad+"  echo \"*** ACCIONES A REALIZAR ***\"\n"
cad=cad+"  echo \"Comprobar y Borrar archivos\"\n"
cad=cad+"  echo \"Ampliacion de la particion o cambio del Disco Duro\"\n"
cad=cad+"fi\n"
oFaultDef.function=cad
oFaultDef.save()
print "FaultDef (add LOW SYSTEM PARTITION SPACE)"


#ATTRIBUTES
oProperty=Property.objects.get(prefix="ALL")
oAttribute=Attribute()
oAttribute.value=oProperty.name
oAttribute.property_att=oProperty
oAttribute.description=""
oAttribute.save()
print "Attribute (add ALL - ALL SYSTEMS)"

oProperty=Property.objects.get(prefix="CTX")
oAttribute=Attribute()
oAttribute.value="RYS.AYTOZAR"
oAttribute.property_att=oProperty
oAttribute.description=""
oAttribute.save()
print "Attribute (add CTX - RYS.AYTOZAR)"

oProperty=Property.objects.get(prefix="CTX")
oAttribute=Attribute()
oAttribute.value="IYD.AYTOZAR"
oAttribute.property_att=oProperty
oAttribute.description=""
oAttribute.save()
print "Attribute (add CTX - IYD.AYTOZAR)"

oProperty=Property.objects.get(prefix="CTX")
oAttribute=Attribute()
oAttribute.value="MODERNIZACION.AYTOZAR"
oAttribute.property_att=oProperty
oAttribute.description=""
oAttribute.save()
print "Attribute (add CTX - MODERNIZACION.AYTOZAR)"

oProperty=Property.objects.get(prefix="CTX")
oAttribute=Attribute()
oAttribute.value="AYTOZAR"
oAttribute.property_att=oProperty
oAttribute.description=""
oAttribute.save()
print "Attribute (add CTX - AYTOZAR)"


oSchedule=Schedule()
oSchedule.name="STANDARD"
oSchedule.description="Default schedule. By context."
oSchedule.save()
print "Schedule (add STANDARD)"

oSchedule=Schedule()
oSchedule.name="SLOW"
oSchedule.description="By context, slowly."
oSchedule.save()
print "Schedule (add SLOW)"


# DELAYS
oScheduleDelay=ScheduleDelay()
oScheduleDelay.delay = 3 
oScheduleDelay.schedule=Schedule.objects.get(name="STANDARD") 
#oScheduleDelay.attributes.add(Attribute.objects.get(name="RYS.AYTOZAR").id,)
oScheduleDelay.save()
oScheduleDelay.attributes.add(Attribute.objects.get(value="RYS.AYTOZAR").id)
oScheduleDelay.save()
print "ScheduleDelay (add 3 STANDARD)"

oScheduleDelay=ScheduleDelay()
oScheduleDelay.delay = 6 
oScheduleDelay.schedule=Schedule.objects.get(name="STANDARD") 
oScheduleDelay.save()
oScheduleDelay.attributes.add(Attribute.objects.get(value="IYD.AYTOZAR").id,)
oScheduleDelay.save()
print "ScheduleDelay (add 6 STANDARD)"

oScheduleDelay=ScheduleDelay()
oScheduleDelay.delay = 9 
oScheduleDelay.schedule=Schedule.objects.get(name="STANDARD") 
oScheduleDelay.save()
oScheduleDelay.attributes.add(Attribute.objects.get(value="AYTOZAR").id,)
oScheduleDelay.save()
print "ScheduleDelay (add 9 STANDARD)"

oScheduleDelay=ScheduleDelay()
oScheduleDelay.delay = 12 
oScheduleDelay.schedule=Schedule.objects.get(name="STANDARD") 
oScheduleDelay.save()
oScheduleDelay.attributes.add(Attribute.objects.get(value="ALL SYSTEMS").id,)
oScheduleDelay.save()
print "ScheduleDelay (add 12 STANDARD)"

# DEVICES
oDeviceManufacturer=DeviceManufacturer()
oDeviceManufacturer.name="EPSON"
oDeviceManufacturer.save()
print "DeviceManufacturer (add EPSON)"

oDeviceManufacturer=DeviceManufacturer()
oDeviceManufacturer.name="FUJITSU"
oDeviceManufacturer.save()
print "DeviceManufacturer (add FUJITSU)"

oDeviceManufacturer=DeviceManufacturer()
oDeviceManufacturer.name="HP"
oDeviceManufacturer.save()
print "DeviceManufacturer (add HP)"

oDeviceManufacturer=DeviceManufacturer()
oDeviceManufacturer.name="CANON"
oDeviceManufacturer.save()
print "DeviceManufacturer (add HP)"

oDeviceType=DeviceType()
oDeviceType.name="SCANNER"
oDeviceType.save()
print "DeviceType (add SCANNER)"

oDeviceConnection=DeviceConnection()
oDeviceConnection.name="USB"
oDeviceConnection.fields=""
oDeviceConnection.devicetype=oDeviceType
oDeviceConnection.code="echo HERE-CODE-SCANNER-USB"
oDeviceConnection.save()
print "DeviceConnection (add USB SCANNER)"


oDeviceConnection=DeviceConnection()
oDeviceConnection.name="TCP"
oDeviceConnection.fields="IP"
oDeviceConnection.devicetype=oDeviceType
oDeviceConnection.code="echo HERE-CODE-SCANNER-LPT"
oDeviceConnection.save()
print "DeviceConnection (add TCP SCANNER)"


oDeviceType=DeviceType()
oDeviceType.name="PRINTER"
oDeviceType.save()
print "DeviceType (add PRINTER)"

oDeviceConnection=DeviceConnection()
oDeviceConnection.name="USB"
oDeviceConnection.fields=""
oDeviceConnection.devicetype=oDeviceType
oDeviceConnection.code="/usr/sbin/lpadmin -p $_MODEL -P $_FILE -v usb:/dev/usb/lp0 -E"
oDeviceConnection.save()
print "DeviceConnection (add USB PRINTER)"

oDeviceConnection=DeviceConnection()
oDeviceConnection.name="LPT (tipix)"
oDeviceConnection.fields=""
oDeviceConnection.devicetype=oDeviceType
oDeviceConnection.code="/usr/sbin/lpadmin -p tipix -v parallel:/dev/lp0 -E"
oDeviceConnection.save()
print "DeviceConnection (add LPT (tipix) PRINTER)"

oDeviceConnection=DeviceConnection()
oDeviceConnection.name="LPT"
oDeviceConnection.fields=""
oDeviceConnection.devicetype=oDeviceType
oDeviceConnection.code="/usr/sbin/lpadmin -p $_MODEL -P $_FILE -v parallel:/dev/lp0 -E"
oDeviceConnection.save()
print "DeviceConnection (add LPT PRINTER)"

oDeviceConnection=DeviceConnection()
oDeviceConnection.name="TCP"
oDeviceConnection.fields="IP"
oDeviceConnection.devicetype=oDeviceType
oDeviceConnection.code="/usr/sbin/lpadmin -p $_MODEL -P $_FILE -v socket://$_IP:9100 -E"
oDeviceConnection.save()
print "DeviceConnection (add TCP PRINTER)"

oDeviceConnection=DeviceConnection()
oDeviceConnection.name="TCP:9101"
oDeviceConnection.fields="IP"
oDeviceConnection.devicetype=oDeviceType
oDeviceConnection.code="/usr/sbin/lpadmin -p $_MODEL -P $_FILE -v socket://$_IP:9101 -E"
oDeviceConnection.save()
print "DeviceConnection (add TCP:9101 PRINTER)"

oDeviceConnection=DeviceConnection()
oDeviceConnection.name="TCP:9102"
oDeviceConnection.fields="IP"
oDeviceConnection.devicetype=oDeviceType
oDeviceConnection.code="/usr/sbin/lpadmin -p $_MODEL -P $_FILE -v socket://$_IP:9102 -E"
oDeviceConnection.save()
print "DeviceConnection (add TCP:9102 PRINTER)"

oDeviceModel=DeviceModel()
oDeviceModel.name="EPL-N2550"
oDeviceModel.manufacturer=DeviceManufacturer.objects.get(name="EPSON")
oDeviceModel.devicetype = oDeviceType
oDeviceModel.filename = "/usr/share/cups/model/Epson/EPL-N2500PS-Postscript.ppd.gz"
oDeviceModel.precode = "# HERE-PRECODE-MODEL-"+oDeviceModel.name
oDeviceModel.postcode = "# HERE-POSTCODE-MODEL-"+oDeviceModel.name
oDeviceModel.save()
oDeviceModel.connections.add(DeviceConnection.objects.get(name="USB",devicetype=2).id)
oDeviceModel.connections.add(DeviceConnection.objects.get(name="TCP",devicetype=2).id)
oDeviceModel.save()
print "DeviceModel (add EPL-N2550)"


oDeviceModel=DeviceModel()
oDeviceModel.name="EPL-5400"
oDeviceModel.manufacturer=DeviceManufacturer.objects.get(name="EPSON")
oDeviceModel.devicetype = oDeviceType
oDeviceModel.filename = "/usr/share/cups/model/Epson/EPL-N2500PS-Postscript.ppd.gz"
oDeviceModel.precode = "# HERE-PRECODE-MODEL-"+oDeviceModel.name
oDeviceModel.postcode = "# HERE-POSTCODE-MODEL-"+oDeviceModel.name
oDeviceModel.save()
oDeviceModel.connections.add(DeviceConnection.objects.get(name="LPT",devicetype=2).id)
oDeviceModel.save()
print "DeviceModel (add EPL-5400)"


oDeviceModel=DeviceModel()
oDeviceModel.name="IRC-5000"
oDeviceModel.manufacturer=DeviceManufacturer.objects.get(name="CANON")
oDeviceModel.devicetype = oDeviceType
oDeviceModel.filename = "/usr/share/cups/model/Epson/EPL-N2500PS-Postscript.ppd.gz"
oDeviceModel.precode = "# HERE-PRECODE-MODEL-"+oDeviceModel.name
oDeviceModel.postcode = "# HERE-POSTCODE-MODEL-"+oDeviceModel.name
oDeviceModel.save()
oDeviceModel.connections.add(DeviceConnection.objects.get(name="TCP",devicetype=2).id)
oDeviceModel.save()
print "DeviceModel (add IRC-5000)"



#QUERIES
oQuery=Query()
oQuery.name = "QUERIES"
oQuery.description = "LIST OF QUERIES"
oQuery.code="if parameters['id']=='':\n    query=Query.objects.all()\nelse:\n    query=Query.objects.filter(id=parameters['id'])\nfields= ('id','name','description','code','parameters')"
oQuery.parameters="def  formParams():\n    from migasfree.system.forms import ParametersForm\n    class myForm(ParametersForm):\n        id = forms.CharField()\n    return myForm"
oQuery.save()
print "Query (add QUERIES)"

oQuery=Query()
oQuery.name = "PACKAGES/SETS"
oQuery.description = "LIST OF PACKAGES/SETS"
oQuery.code = "query=Package.objects.filter(name__contains=parameters[\"name\"])\nfields=('id','name','store__name')\ntitles=('id','name','store')"
oQuery.parameters="def  formParams():\n    from migasfree.system.forms import ParametersForm\n    class myForm(ParametersForm):\n        name = forms.CharField()\n    return myForm"

oQuery.save()
print "Query (add PACKAGES/SETS)"

oQuery=Query()
oQuery.name = "COMPUTERS BY ATTRIBUTES"
oQuery.description = "LIST THE COMPUTERS THAT HAVE A DETERMINATE ATTRIBUTE"
oQuery.code = "query=Login.objects.filter(attributes__property_att__id=parameters[\"property_att\"],attributes__value__contains=parameters[\"value\"])\nfields=('computer__name','user__name','date',)\ntitles=('computer','user','date of login',)"
oQuery.parameters="def  formParams():\n    from migasfree.system.forms import ParametersForm\n    class myForm(ParametersForm):\n        property_att=forms.ModelChoiceField(Property.objects.all())\n        value = forms.CharField()\n    return myForm"
oQuery.save()
print "Query (add COMPUTERS BY ATTRIBUTES)"


oQuery=Query()
oQuery.name = "COMPUTERS WITH THE PACKAGE..."
oQuery.description = "LIST THE COMPUTERS WITH THE PACKAGE ESPECIFIQUED"
oQuery.code = "query=Computer.objects.filter(software__contains=parameters['package'])\nfields=('id','name','ip')\ntitles=('id','name','ip')"
oQuery.parameters="def  formParams():\n    from migasfree.system.forms import ParametersForm\n    class myForm(ParametersForm):\n        package = forms.CharField()\n    return myForm"
oQuery.save()
print "Query (add COMPUTERS WITH THE PACKAGE...)"

oQuery=Query()
oQuery.name = "PACKAGE/SET ORPHAN"
oQuery.description = "PACKAGES/SET THAT NOT HAVE BEEN ASIGNED TO A REPOSITORY "
oQuery.code = "query=Package.objects.version(0).filter(Q(repository__id__exact=None))\nfields=('id','version__name','store__name','name')\ntitles=('id','version','store','package/set')"
oQuery.parameters=""
oQuery.save()
print "Query (add PACKAGE/SET ORPHAN)"

oQuery=Query()
oQuery.name = "REPOSITORIES WITH A PACKAGE/SET"
oQuery.description = "LIST THE REPOSITORIES THAT HAVE ASIGNNED A DETERMINATE PACKAGE/SET "
oQuery.code = "query=Repository.objects.filter(version=VERSION).filter(Q(packages__name__contains=parameters['package'])).extra(select={'package': 'system_package.name',})\nfields=('id','name','package')\ntitles=('id','Repository','Package',)"
oQuery.parameters="def  formParams():\n    from migasfree.system.forms import ParametersForm\n    class myForm(ParametersForm):\n        package = forms.CharField()\n    return myForm"
oQuery.save()
print "Query (add REPOSITORIES WITH A PACKAGE/SET)"


oQuery=Query()
oQuery.name = "LAST LOGIN"
oQuery.description = "LIST OF MESSAGES FROM COMPUTERS"
oQuery.code = "query=Login.objects.values('computer_id').annotate(lastdate=Max('date')).order_by('lastdate')\nfields=('computer__name','computer__ip','lastdate')\ntitles=('computer','ip','lastdate')\n"
oQuery.parameters=""
oQuery.save()
print "Query (add LAST LOGIN)"






#GROUPS
oGroupRead=Group()
oGroupRead.name="Read"
oGroupRead.save()
oGroupRead.permissions.add(Permission.objects.get(codename="change_computer").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_device").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_user",content_type__app_label="system").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_login").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_attribute").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_error").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_fault").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_deviceconnection").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_devicemanufacturer").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_devicemodel").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_devicetype").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_schedule").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_scheduledelay").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_autocheckerror").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_faultdef").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_property").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_checking").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_version").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_pms").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_variable").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_query").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_package").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_repository").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_store").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_message",content_type__app_label="system").id)
oGroupRead.permissions.add(Permission.objects.get(codename="change_update").id)
oGroupRead.save()



oGroupRepo=Group()
oGroupRepo.name="Change Software Configuration"
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


oGroupPackager=Group()
oGroupPackager.name="Packager"
oGroupPackager.save()
oGroupPackager.permissions.add(Permission.objects.get(codename="add_package").id)
oGroupPackager.permissions.add(Permission.objects.get(codename="change_package").id)
oGroupPackager.permissions.add(Permission.objects.get(codename="can_save_package").id)
oGroupPackager.permissions.add(Permission.objects.get(codename="delete_package").id)
oGroupPackager.permissions.add(Permission.objects.get(codename="add_store").id)
oGroupPackager.permissions.add(Permission.objects.get(codename="change_store").id)
oGroupPackager.permissions.add(Permission.objects.get(codename="can_save_store").id)
oGroupPackager.permissions.add(Permission.objects.get(codename="delete_store").id)
oGroupPackager.save()



oGroupCheck=Group()
oGroupCheck.name="Check"
oGroupCheck.save()
oGroupCheck.permissions.add(Permission.objects.get(codename="add_autocheckerror").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="change_autocheckerror").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="can_save_autocheckerror").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="delete_autocheckerror").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="add_error").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="change_error").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="can_save_error").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="delete_error").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="add_fault").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="change_fault").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="can_save_fault").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="delete_fault").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="add_message",content_type__app_label="system").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="change_message",content_type__app_label="system").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="can_save_message",content_type__app_label="system").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="delete_message",content_type__app_label="system").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="add_update").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="change_update").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="can_save_update").id)
oGroupCheck.permissions.add(Permission.objects.get(codename="delete_update").id)
oGroupCheck.save()

oGroupDev=Group()
oGroupDev.name="Devices"
oGroupDev.save()
oGroupDev.permissions.add(Permission.objects.get(codename="add_deviceconnection").id)
oGroupDev.permissions.add(Permission.objects.get(codename="change_deviceconnection").id)
oGroupDev.permissions.add(Permission.objects.get(codename="can_save_deviceconnection").id)
oGroupDev.permissions.add(Permission.objects.get(codename="delete_deviceconnection").id)
oGroupDev.permissions.add(Permission.objects.get(codename="add_devicemanufacturer").id)
oGroupDev.permissions.add(Permission.objects.get(codename="change_devicemanufacturer").id)
oGroupDev.permissions.add(Permission.objects.get(codename="can_save_devicemanufacturer").id)
oGroupDev.permissions.add(Permission.objects.get(codename="delete_devicemanufacturer").id)
oGroupDev.permissions.add(Permission.objects.get(codename="add_devicemodel").id)
oGroupDev.permissions.add(Permission.objects.get(codename="change_devicemodel").id)
oGroupDev.permissions.add(Permission.objects.get(codename="can_save_devicemodel").id)
oGroupDev.permissions.add(Permission.objects.get(codename="delete_devicemodel").id)
oGroupDev.permissions.add(Permission.objects.get(codename="add_devicetype").id)
oGroupDev.permissions.add(Permission.objects.get(codename="change_devicetype").id)
oGroupDev.permissions.add(Permission.objects.get(codename="can_save_devicetype").id)
oGroupDev.permissions.add(Permission.objects.get(codename="delete_devicetype").id)
oGroupDev.save()

oGroupQuery=Group()
oGroupQuery.name="Query"
oGroupQuery.save()
oGroupQuery.permissions.add(Permission.objects.get(codename="add_query").id)
oGroupQuery.permissions.add(Permission.objects.get(codename="change_query").id)
oGroupQuery.permissions.add(Permission.objects.get(codename="can_save_query").id)
oGroupQuery.permissions.add(Permission.objects.get(codename="delete_query").id)
oGroupQuery.save()

oGroupSys=Group()
oGroupSys.name="System"
oGroupSys.save()
oGroupSys.permissions.add(Permission.objects.get(codename="add_checking").id)
oGroupSys.permissions.add(Permission.objects.get(codename="change_checking").id)
oGroupSys.permissions.add(Permission.objects.get(codename="can_save_checking").id)
oGroupSys.permissions.add(Permission.objects.get(codename="delete_checking").id)
oGroupSys.permissions.add(Permission.objects.get(codename="add_faultdef").id)
oGroupSys.permissions.add(Permission.objects.get(codename="change_faultdef").id)
oGroupSys.permissions.add(Permission.objects.get(codename="can_save_faultdef").id)
oGroupSys.permissions.add(Permission.objects.get(codename="delete_faultdef").id)
oGroupSys.permissions.add(Permission.objects.get(codename="add_property").id)
oGroupSys.permissions.add(Permission.objects.get(codename="change_property").id)
oGroupSys.permissions.add(Permission.objects.get(codename="can_save_property").id)
oGroupSys.permissions.add(Permission.objects.get(codename="delete_property").id)
oGroupSys.permissions.add(Permission.objects.get(codename="add_pms").id)
oGroupSys.permissions.add(Permission.objects.get(codename="change_pms").id)
oGroupSys.permissions.add(Permission.objects.get(codename="can_save_pms").id)
oGroupSys.permissions.add(Permission.objects.get(codename="delete_pms").id)
#oGroupSys.permissions.add(Permission.objects.get(codename="add_variable").id)
oGroupSys.permissions.add(Permission.objects.get(codename="change_variable").id)
oGroupSys.permissions.add(Permission.objects.get(codename="can_save_variable").id)
#oGroupSys.permissions.add(Permission.objects.get(codename="delete_variable").id)
oGroupSys.permissions.add(Permission.objects.get(codename="add_version").id)
oGroupSys.permissions.add(Permission.objects.get(codename="change_version").id)
oGroupSys.permissions.add(Permission.objects.get(codename="can_save_version").id)
oGroupSys.permissions.add(Permission.objects.get(codename="delete_version").id)

oGroupSys.permissions.add(Permission.objects.get(codename="add_message",content_type__app_label="system").id)
oGroupSys.permissions.add(Permission.objects.get(codename="change_message",content_type__app_label="system").id)
oGroupSys.permissions.add(Permission.objects.get(codename="can_save_message",content_type__app_label="system").id)
oGroupSys.permissions.add(Permission.objects.get(codename="delete_message",content_type__app_label="system").id)
oGroupSys.permissions.add(Permission.objects.get(codename="add_update").id)
oGroupSys.permissions.add(Permission.objects.get(codename="change_update").id)
oGroupSys.permissions.add(Permission.objects.get(codename="can_save_update").id)
oGroupSys.permissions.add(Permission.objects.get(codename="delete_update").id)


oGroupSys.save()


#USERS

oUser=UserProfile()
oUser.username ="admin"
oUser.is_staff=True
oUser.is_active=True
oUser.is_superuser=True
oUser.version=oVersion
oUser.set_password("admin")
oUser.save()

oUser=UserProfile()
oUser.username ="system"
oUser.is_staff=True
oUser.is_active=True
oUser.is_superuser=False
oUser.version=oVersion
oUser.set_password("system")
oUser.save()
oUser.groups.add(oGroupRead.id)
oUser.groups.add(oGroupSys.id)
oUser.save()

oUser=UserProfile()
oUser.username ="device"
oUser.is_staff=True
oUser.is_active=True
oUser.is_superuser=False
oUser.version=oVersion
oUser.set_password("device")
oUser.save()
oUser.groups.add(oGroupRead.id)
oUser.groups.add(oGroupDev.id)
oUser.save()

oUser=UserProfile()
oUser.username ="query"
oUser.is_staff=True
oUser.is_active=True
oUser.is_superuser=False
oUser.version=oVersion
oUser.set_password("query")
oUser.save()
oUser.groups.add(oGroupRead.id)
oUser.groups.add(oGroupQuery.id)
oUser.save()


oUser=UserProfile()
oUser.username ="packager"
oUser.is_staff=True
oUser.is_active=True
oUser.is_superuser=False
oUser.version=oVersion
oUser.set_password("packager")
oUser.save()
oUser.groups.add(oGroupRead.id)
oUser.groups.add(oGroupPackager.id)
oUser.save()



oUser=UserProfile()
oUser.username ="repo"
oUser.is_staff=True
oUser.is_active=True
oUser.is_superuser=False
oUser.version=oVersion
oUser.set_password("repo")
oUser.save()
oUser.groups.add(oGroupRead.id)
oUser.groups.add(oGroupRepo.id)
oUser.save()


oUser=UserProfile()
oUser.username ="check"
oUser.is_staff=True
oUser.is_active=True
oUser.is_superuser=False
oUser.version=oVersion
oUser.set_password("check")
oUser.save()
oUser.groups.add(oGroupRead.id)
oUser.groups.add(oGroupCheck.id)
oUser.save()


oUser=UserProfile()
oUser.username ="read"
oUser.is_staff=True
oUser.is_active=True
oUser.is_superuser=False
oUser.version=oVersion
oUser.set_password("read")
oUser.save()
oUser.groups.add(oGroupRead.id)
oUser.save()




#***********************************************************************************************
def byVersion(oVersion,oPackage1,oPackage2,oPackage3):

    #STORES
    oStore=Store()
    oStore.name="org"
    oStore.version=oVersion
    oStore.save()
    oStore=Store()
    oStore.name="update"
    oStore.version=oVersion
    oStore.save()

    #REPOSITORIES
    print "Creating REPOSITORY 'MIGASFREE-CLIENT' in "+oVersion.name+"..."
    oRepository=Repository()
    oRepository.name="MIGASFREE-CLIENT"
    oRepository.active=True
    oRepository.version=oVersion
    oRepository.date=datetime.now().date()
    oRepository.schedule=Schedule.objects.get(name="STANDARD")
    oRepository.toinstall="migasfree-test"
    oRepository.toremove=""
    oRepository.save()
    oRepository.packages.add(oPackage1,oPackage2)
    oRepository.attributes.add(Attribute.objects.get(value="ALL SYSTEMS"))
    oRepository.save()

    print "Creating REPOSITORY 'MIGASFREE-PACKAGER' in "+oVersion.name+"..."
    oRepository=Repository()
    oRepository.name="MIGASFREE-PACKAGER"
    oRepository.active=True
    oRepository.version=oVersion
    oRepository.date=datetime.now().date()
#    oRepository.schedule=Schedule.objects.get(name="STANDARD")
    oRepository.toinstall="migasfree-packager"
    oRepository.toremove=""
    oRepository.save()
    oRepository.packages.add(oPackage3)
#    oRepository.attributes.add(Attribute.objects.get(name="ALL SYSTEMS"))
    oRepository.save()

    print "Creating REPOSITORIES FILES in "+oVersion.name+"..."
    os.system("http_proxy='';wget -O /tmp/response http://127.0.0.1:80/migasfree/createrepositoriesofpackage/?VER="+oVersion.name+"\&PACKAGE="+oPackage1.name+"\&username=packager\&password=packager 2>/dev/null" )
    os.system("http_proxy='';wget -O /tmp/response http://127.0.0.1:80/migasfree/createrepositoriesofpackage/?VER="+oVersion.name+"\&PACKAGE="+oPackage3.name+"\&username=packager\&password=packager 2>/dev/null" )



def UploadPkg(VERSION,PACKAGE):
    print "\nUploading "+PACKAGE+" en "+VERSION+"..." 
    os.system("curl -x '' -b 'username=packager; password=packager; VER="+VERSION+"; STORE=third/migasfree; NOPKG=' -F file=@"+PACKAGE+" http://127.0.0.1:80/migasfree/uploadPackage/")




VERSION_CLIENT_RPM="-1.0-0.4.noarch.rpm"
#VERSION_CLIENT_DEB="_1.4_all.deb"
VERSION_CLIENT_DEB="-1.0.deb"

VERSION_TEST_RPM="-1.0-0.0.noarch.rpm"
VERSION_TEST_DEB="-1.0.deb"

VERSION_PACKAGER_RPM="-1.0-0.0.noarch.rpm"
VERSION_PACKAGER_DEB="-1.0.deb"


#down packages RPM
os.system("wget --no-cache --no-check-certificate -O /srv/Django/migasfree/utils/db/packages/migasfree-client"+VERSION_CLIENT_RPM+"  https://github.com/agacias/migasfree/raw/master/utils/db/packages/migasfree-client"+VERSION_CLIENT_RPM) 

os.system("wget --no-cache --no-check-certificate -O /srv/Django/migasfree/utils/db/packages/migasfree-test"+VERSION_TEST_RPM+"  https://github.com/agacias/migasfree/raw/master/utils/db/packages/migasfree-test"+VERSION_TEST_RPM) 

os.system("wget --no-cache --no-check-certificate -O /srv/Django/migasfree/utils/db/packages/migasfree-packager"+VERSION_PACKAGER_RPM+" https://github.com/agacias/migasfree/raw/master/utils/db/packages/migasfree-packager"+VERSION_PACKAGER_RPM) 

#down packages DEB
os.system("wget --no-cache --no-check-certificate -O /srv/Django/migasfree/utils/db/packages/migasfree-client"+VERSION_CLIENT_DEB+" https://github.com/agacias/migasfree/raw/master/utils/db/packages/migasfree-client"+VERSION_CLIENT_DEB) 

os.system("wget --no-cache --no-check-certificate -O /srv/Django/migasfree/utils/db/packages/migasfree-test"+VERSION_TEST_DEB+"  https://github.com/agacias/migasfree/raw/master/utils/db/packages/migasfree-test"+VERSION_TEST_DEB) 

os.system("wget --no-cache --no-check-certificate -O /srv/Django/migasfree/utils/db/packages/migasfree-packager"+VERSION_PACKAGER_DEB+" https://github.com/agacias/migasfree/raw/master/utils/db/packages/migasfree-packager"+VERSION_PACKAGER_DEB) 




#UPLOADING PACKAGES
UploadPkg("FEDORA","/srv/Django/migasfree/utils/db/packages/migasfree-client"+VERSION_CLIENT_RPM)
UploadPkg("FEDORA","/srv/Django/migasfree/utils/db/packages/migasfree-test"+VERSION_TEST_RPM)
UploadPkg("FEDORA","/srv/Django/migasfree/utils/db/packages/migasfree-packager"+VERSION_PACKAGER_RPM)

UploadPkg("OPENSUSE","/srv/Django/migasfree/utils/db/packages/migasfree-client"+VERSION_CLIENT_RPM)
UploadPkg("OPENSUSE","/srv/Django/migasfree/utils/db/packages/migasfree-test"+VERSION_TEST_RPM)
UploadPkg("OPENSUSE","/srv/Django/migasfree/utils/db/packages/migasfree-packager"+VERSION_PACKAGER_RPM)

UploadPkg("UBUNTU","/srv/Django/migasfree/utils/db/packages/migasfree-client"+VERSION_CLIENT_DEB)
UploadPkg("UBUNTU","/srv/Django/migasfree/utils/db/packages/migasfree-test"+VERSION_TEST_DEB)
UploadPkg("UBUNTU","/srv/Django/migasfree/utils/db/packages/migasfree-packager"+VERSION_PACKAGER_DEB)

print "\n"

oVersion=Version.objects.get(name="FEDORA")    
oPackage1=Package.objects.get(name="migasfree-client"+VERSION_CLIENT_RPM,version=oVersion)
oPackage2=Package.objects.get(name="migasfree-test"+VERSION_TEST_RPM,version=oVersion)
oPackage3=Package.objects.get(name="migasfree-packager"+VERSION_PACKAGER_RPM,version=oVersion)
byVersion(oVersion,oPackage1,oPackage2,oPackage3)

oVersion=Version.objects.get(name="OPENSUSE")    
oPackage1=Package.objects.get(name="migasfree-client"+VERSION_CLIENT_RPM,version=oVersion)
oPackage2=Package.objects.get(name="migasfree-test"+VERSION_TEST_RPM,version=oVersion)
oPackage3=Package.objects.get(name="migasfree-packager"+VERSION_PACKAGER_RPM,version=oVersion)
byVersion(oVersion,oPackage1,oPackage2,oPackage3)

oVersion=Version.objects.get(name="UBUNTU")    
oPackage1=Package.objects.get(name="migasfree-client"+VERSION_CLIENT_DEB,version=oVersion)
oPackage2=Package.objects.get(name="migasfree-test"+VERSION_TEST_DEB,version=oVersion)
oPackage3=Package.objects.get(name="migasfree-packager"+VERSION_PACKAGER_DEB,version=oVersion)
byVersion(oVersion,oPackage1,oPackage2,oPackage3)






#***********************************************************************************************
#Server Files:
os.system("wget --no-cache --no-check-certificate -O /var/www/htdocs/repo/chart/expressInstall.swf https://github.com/agacias/migasfree/raw/master/utils/htdocs/repo/chart/expressInstall.swf")

os.system("wget --no-cache --no-check-certificate -O /var/www/htdocs/repo/chart/open-flash-chart.swf https://github.com/agacias/migasfree/raw/master/utils/htdocs/repo/chart/open-flash-chart.swf")

os.system("wget --no-cache --no-check-certificate -O /var/www/htdocs/repo/chart/swfobject.js https://github.com/agacias/migasfree/raw/master/utils/htdocs/repo/chart/swfobject.js")



os.system("wget --no-cache --no-check-certificate -O /var/www/htdocs/repo/icons/computer_alert.png https://github.com/agacias/migasfree/raw/master/utils/htdocs/repo/icons/computer_alert.png") 

os.system("wget --no-cache --no-check-certificate -O /var/www/htdocs/repo/icons/chart.png https://github.com/agacias/migasfree/raw/master/utils/htdocs/repo/icons/chart.png") 


