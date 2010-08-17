# -*- encoding: utf-8 -*-

from django.utils.translation import ugettext as _

from migasfree.system.models import Pms
from migasfree.system.models import Version
from migasfree.system.models import Computer

from migasfree.system.models import User

from migasfree.system.models import Repository
from migasfree.system.models import Login
from migasfree.system.models import Variable
from migasfree.system.models import Property
from migasfree.system.models import Attribute
from migasfree.system.models import FaultDef
from migasfree.system.models import ScheduleDelay
from migasfree.system.models import Schedule
from migasfree.system.models import Package
from migasfree.system.views import *
from django.db.models import Q
import os
import codecs

from datetime import datetime
from datetime import timedelta


def getVariable(name_variable):
    return Variable.objects.get(name=name_variable).value

# Add a attribute to the system. Par is a "value~name" string or only "valor" 
def auto_attribute(oProperty,par):


    reg=par.split("~")

    value_att=reg[0]
    if len(reg)>1:
        description_att=reg[1]
    else:
        description_att=""
    
    
    if value_att <> "":  
        try:
            oAttribute=Attribute.objects.get(value=value_att,property_att__id=oProperty.id)
        except: # if not exist the attribute, we add it 
            if oProperty.auto == True:
                oAttribute=Attribute()
                oAttribute.property_att=oProperty
                oAttribute.value=value_att
                oAttribute.description=description_att
                oAttribute.save()      


def horizon(mydate, delay):
    """No weekends"""
    iday=int(mydate.strftime("%w"))
    idelta=delay+(((delay+iday-1)/5)*2)
    return mydate+timedelta(days=idelta)


# process the file attributes.xml and return a script bash for be execute in the client
def process_attributes(request,file):

    import xml.dom.minidom
    from xml.dom.minidom import Node


    import time
    t=time.strftime("%Y-%m-%d")
    m=time.strftime("%Y-%m-%d %H:%M:%S")

#    ip=request.META['REMOTE_ADDR']

    doc = xml.dom.minidom.parse(file)

    dic_computer={} # Dictionary of computer
    lst_attributes=[] # List of attributes of computer

    ret=""

    # Loop the file
    for s in doc.childNodes:
     for n in s.childNodes:

      if n.nodeName == "COMPUTER": 
        for e in n.childNodes:
          if e.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
            try:
                dic_computer[e.nodeName]= e.firstChild.data  
            except:
               pass   



        if dic_computer["HOSTNAME"]=="desktop":
          strError=_('desktop is not valid name for this computer: IP=%(ip)s') % {'ip': p}
          oError=Error()
          oError.computer=Computer.objects.get(name="desktop")
          oError.date=m
          oError.error=strError
          oError.save()
          return HttpResponse("# "+strError+"\n",mimetype='text/plain')


        #registration of ip and version of computer
        try:
          oComputer=Computer.objects.get(name=dic_computer["HOSTNAME"])
          oComputer.ip=dic_computer["IP"]
          oComputer.version=Version.objects.get(name=dic_computer["VERSION"])
          oComputer.save()
        except: # if not exists the computer, we add it
          oComputer=Computer(name=dic_computer["HOSTNAME"])
          oComputer.dateinput=t
          oComputer.ip=dic_computer["IP"]
          oComputer.version=Version.objects.get(name=dic_computer["VERSION"])
          oComputer.save()    


        # if not exists the user, we add it
        try:
          oUser=User.objects.get(name=dic_computer["USER"])
        except:
          oUser=User()
          oUser.name=dic_computer["USER"]
          oUser.fullname=dic_computer["USER_FULLNAME"]
          oUser.save()
 

        # Save Login
        SaveLogin(dic_computer["HOSTNAME"],dic_computer["USER"])
        oLogin=Login.objects.get(computer=Computer.objects.get(name=dic_computer["HOSTNAME"]),user=User.objects.get(name=dic_computer["USER"]))

        # Get version
        version=dic_computer["VERSION"]

        oVersion=Version.objects.get(name=version)

        # Get the Package Management System
        oPms=Pms.objects.get(id=oVersion.pms.id)


      if n.nodeName == "ATTRIBUTES":
        for e in n.childNodes:
          if e.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:

               oProperty=Property.objects.get(prefix=e.nodeName)
               try:
                   data=e.firstChild.data

                   # we execute the before_insert function
                   if oProperty.before_insert<>"":
                       exec(oProperty.before_insert.replace("\r","")) 
                     
	               # NORMAL
                   if oProperty.kind == "N":
                       lst_attributes.append(data)                       
                       auto_attribute(oProperty,data)
                       oLogin.attributes.add(Attribute.objects.get(value=data))


                   # LIST            
                   if oProperty.kind == "-":
                       lista=data.split(",")
                       for elemento_lista in lista:
                           lst_attributes.append(data)
                           auto_attribute(oProperty,elemento_lista)  
                           oLogin.attributes.add(Attribute.objects.get(value=elemento_lista.split("~")[0]))

                   # ADDS RIGHT            
                   if oProperty.kind == "R":
                       lista=data.split(".")
                       c=data
                       l=0
                       for x in lista:
                           lst_attributes.append(c[l:])
                           auto_attribute(oProperty,c[l:])
                           oLogin.attributes.add(Attribute.objects.get(value=c[l:]))                   
                           l=l+len(x)+1


                   # ADDS LEFT
                   if oProperty.kind == "L":
                       lista=data.split(".")
                       c=data
                       l=0
                       for x in lista:
                           l=l+len(x)+1
                           lst_attributes.append(c[0:l-1])
                           auto_attribute(oProperty,c[0:l-1])  
                           oLogin.attributes.add(Attribute.objects.get(value=c[0:l-1]))                  

                   # we execute the after_insert function
                   if oProperty.after_insert<>"":
                       exec(oProperty.after_insert.replace("\r","")) 

               except:		           
                   pass
 


      if n.nodeName == "FAULTS":
        
        for e in n.childNodes:
          if e.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
               oFaultDef=FaultDef.objects.get(name=e.nodeName)
               try:
                   data=e.firstChild.data
                   # we add the fault
                   oFault=Fault()
                   oFault.computer=oComputer
                   oFault.date=m
                   oFault.text=data
                   oFault.faultdef=oFaultDef
                   oFault.save()

               except:		           
                   pass




    dic_repos={}

    repositories=Repository.objects.filter(Q(attributes__value__in=lst_attributes),Q(version__id=oVersion.id)) 
    repositories==repositories.filter(Q(modified=False),Q(version__id=oVersion.id),Q(active=True))

    for r in repositories:
        dic_repos[r.name]=r.id

    repositories=Repository.objects.filter(Q(schedule__scheduledelay__attributes__value__in=lst_attributes),Q(active=True))
    repositories==repositories.filter(Q(modified=False),Q(version__id=oVersion.id),Q(active=True))
    repositories=repositories.extra(select={'delay': "system_scheduledelay.delay",})     

    for r in repositories:
        if horizon(r.date,r.delay)<=datetime.now().date():
            dic_repos[r.name]=r.id


    repositories=Repository.objects.filter(Q(id__in=dic_repos.values()) )


    #SCRIPT FOR THE COMPUTER
    ret="#!/bin/bash\n\n"

    ret=ret+"function icon_tooltip {\n"
    ret=ret+"  echo \"tooltip: $1\" >&3\n"
    ret=ret+"}\n\n"

    ret=ret+". /usr/share/migasfree/init\n\n"
    ret=ret+"_FILE_LOG=\"$_DIR_TMP/history_sw.log\"\n"
    ret=ret+"_FILE_ERR=\"$_DIR_TMP/migasfree.err\"\n"
    ret=ret+"_FILE_INV_HW=\"$_DIR_TMP/inventory.dat\"\n"

    ret=ret+"\n\n# 1.- PRESERVE INITIAL DATE\n"
    ret=ret+"_INI=`date +'%d-%m-%Y %k:%M:%S'`\n"

    ret=ret+"\n\n# 2.- IF HAVE BEEN INSTALED PACKAGES MANUALITY THE INFORMATION IS UPLOAD TO migasfree server\n"
    ret=ret+"soft_history $_FILE_LOG.1 $_FILE_LOG.0 $_FILE_LOG \"\"\n"

    ret=ret+"\n\n# 3.- If WE HAVE OLD ERRORS, WE UPLOAD ITS TO migasfree SERVER\n" 
    ret=ret+"directupload $_FILE_ERR 2>>$_FILE_ERR\n"
    
    ret=ret+"\n\n# 4.- SAVE REPOSITORIES\n"
    s=_("Creating Repositories")
    ret=ret+"icon_tooltip \""+ s +"\"\n"
    ret=ret+SaveRepositories(repositories,oVersion,oPms) 

    ret=ret+"\n\n# 5.- CLEAN CACHE OF PACKAGE MANAGEMENT SYSTEM\n"
    ret=ret+"icon_tooltip \""+ _("Refresh cache") +"\"\n" 
    ret=ret+"pms_cleanall 2>>$_FILE_ERR\n"

    ret=ret+"\n\n# 6.- REMOVE PACKAGES\n"
    ret=ret+"icon_tooltip \""+ _("Checking packages to remove") +"\"\n" 
    cPackages=""
    for d in repositories:
        if not d.toremove=="": 
            cPackages=cPackages+" "+d.toremove
    if not cPackages=="":
        ret=ret+"icon_tooltip \""+ _("Removing packages") +"\"\n" 
        ret=ret+"pms_remove_silent \""+cPackages+"\" 2>> $_FILE_ERR\n"

    ret=ret+"\n\n# 7.- INSTALL PACKAGES\n"
    ret=ret+"icon_tooltip \""+ _("Checking packages to install") +"\"\n"
    cPackages="" 
    for d in repositories:
        if not d.toinstall=="": 
            cPackages=cPackages+" "+d.toinstall
    if not cPackages=="":
        ret=ret+"icon_tooltip \""+ _("Installing packages") +"\"\n" 
        ret=ret+"pms_install_silent \""+cPackages+"\" 2>> $_FILE_ERR\n"

    ret=ret+"\n\n# 8.- UPDATE PACKAGES\n"
    ret=ret+"icon_tooltip \""+ _("Updating packages") +"\"\n" 
    ret=ret+"pms_update_silent 2>> $_FILE_ERR\n"


    ret=ret+"\n\n# 9.- UPLOAD THE SOFTWARE HISTORY\n"
    ret=ret+"icon_tooltip \""+ _("Upload changes of software") +"\"\n" 
    ret=ret+"soft_history $_FILE_LOG.0 $_FILE_LOG.1 $_FILE_LOG \"$_INI\"\n"

    ret=ret+"\n\n# 10.- UPLOAD THE SOFTWARE INVENTORY\n"
    ret=ret+"icon_tooltip \""+ _("Upload inventory software") +"\"\n" 
    # If is the Computer with de Software Base we upload the list of packages
    if oVersion.computerbase==oComputer.name:
      ret=ret+"cp $_FILE_LOG.1 $_DIR_TMP/base.log\n"
      ret=ret+"directupload $_DIR_TMP/base.log 2>> $_FILE_ERR\n"
    #Get the software base of the version and upload the diff 
    ret=ret+"download_file \"softwarebase/?VERSION=$MIGASFREE_VERSION\" \"$_DIR_TMP/softwarebase.log\" 2>/dev/null\n" 
    ret=ret+"soft_inventory $_DIR_TMP/softwarebase.log $_FILE_LOG.1 $_DIR_TMP/software.log\n"

    ret=ret+"\n\n# 11.- UPDATE THE HARDWARE INVENTORY\n"
    ret=ret+"icon_tooltip \""+ _("Upload inventory hardware") +"\"\n" 
    oComputer=Computer.objects.get(name=dic_computer["HOSTNAME"])
    ret=ret+"/usr/bin/python /usr/local/bin/inventario.py 2>> $_FILE_ERR\n"
    ret=ret+"directupload $_FILE_INV_HW 2>> $_FILE_ERR\n"

    ret=ret+"\n\n\n# 12.- UPLOAD ERRORS OF 'migasfree -u' TO migasfree\n"
    ret=ret+"icon_tooltip \""+ _("Upload errors") +"\"\n" 
    ret=ret+"directupload $_FILE_ERR 2>> $_FILE_ERR\n"

#    ret=ret+"\n\n# 13.- NOTIFY USER\n"
#    ret=ret+"icon_tooltip \""+ _("Notify user") +"\"\n" 
#    ret=ret+"echo \"tooltip: System is updated.\" >&3\n"
#    ret=ret+"DISPLAY=$_DISPLAY_GRAPHIC zenity --text-info --title=\"migasfree\" --filename=\"/home/alberto/Escritorio/info.txt\""

#    ret=ret+"DISPLAY=$_DISPLAY_GRAPHIC notify-send --expire-time=0 --icon /usr/share/icons/hicolor/48x48/apps/migasfree.png 'REDES Y SISTEMAS' 'Se ha instalado bluefish'\n"
#    ret=ret+"DISPLAY=$_DISPLAY_GRAPHIC evince /home/alberto/bluefish.pdf\n"
#    ret=ret+"gnomesu -c 'evince -s /home/alberto/notification.pdf' -u alberto &\n"
#    ret=ret+"DISPLAY=$_DISPLAY_GRAPHIC gnomesu -c 'ooimpress -show /home/alberto/notification.odp' -u alberto &\n"
#    ret=ret+"echo \"message: You must reboot the computer\" >&3"


    ret=ret+"icon_tooltip \""+ _("System is updated") +"\"\n" 
    ret=ret+"sleep 3\n" 

    return ret


def SaveLogin(pc,user):
    import time
    m=time.strftime("%Y-%m-%d %H:%M:%S")
    try:
       oLogin=Login.objects.get(computer=Computer.objects.get(name=pc),user=User.objects.get(name=user))
       oLogin.date=m
       oLogin.save()
    except: # if Login not exist, we save it
       oLogin=Login(computer=Computer.objects.get(name=pc),user=User.objects.get(name=user))
       oLogin.date=m
       oLogin.save()
    return





# Return the content of file of list of repositories
def SaveRepositories(lista,oVersion,oPms): 

    ret="cat > $PMS_SOURCES_FILES << EOF\n"
    # Repositories
    for d in lista:
        cad=oPms.repository+"\n"
	ret=ret+cad.replace("%REPO%",d.name).replace("%VERSION%",oVersion.name)

    ret=ret+"EOF\n"

    return ret


def CreateRepositoriesofPackage(packagename,versionname):
    version=Version.objects.get(name=versionname)
    try:
        package=Package.objects.get(name=packagename,version=version)
        qs=Repository.objects.filter(packages__id=package.id)
        for r in qs:
            r.createpackages=[]
            r.save()
        CreateRepositories(package.version.id)
    except:
        pass

def compare_values(v1,v2):
    i=0
    if len(v1)<>len(v2):
        return False
    for x in v1:
        print v1[i]
        print v2[i]
        if not v1[i] in v2:
            return False
        i=i+1
    return True

 
def CreateRepositories(version_id): # Crea los repositorios para la version
    import os

    #Get the Package Management System
    oPms=Pms.objects.get(id=version_id)
    
    def history(d):
        import time
        t=time.strftime("%Y-%m-%d %H:%m:%S")
        txt=""
        pkgs=d.packages.all()
        for o in pkgs:
            txt= txt+"        "+o.store.name.ljust(10)+" - "+o.name+"\n"
        return txt


    PATH_REPO=getVariable('PATH_REPO')
    _version=Version.objects.get(id=version_id)

    bash=""

    #Set to True the modified field in the repositories that have been change yours packages from last time.
    ds=Repository.objects.filter(version=_version)
    for d in ds:
        if compare_values(d.packages.values("id"),d.createpackages.values("id")):
            d.modified=False
            d.save()
        else:
            r=Repository.objects.get(id=d.id)
            for p in r.createpackages.all():
                r.createpackages.remove(p.id)
            for p in r.packages.all():
                r.createpackages.add(p.id)
            r.modified=True
            r.save()


    #Remove the repositories not active
    ds=Repository.objects.filter(modified=True,active=False,version=_version)
    for d in ds:
        bash=bash+"rm -rf "+PATH_REPO+d.version.name+"/"+oPms.slug+"/"+d.name+"\n"

    #Loop the Repositories modified and active for this version
    ds=Repository.objects.filter(modified=True,active=True,version=_version)
    for d in ds:
        # we remove it
        bash=bash+"rm -rf "+PATH_REPO+d.version.name+"/"+oPms.slug+"/"+d.name+"\n"

    txt="Analyzing the repositories to create files for version: "+_version.name +"\n"

    for d in ds: 
        PATH_STORES=PATH_REPO+d.version.name+"/STORES/" 
        PATH_TMP=PATH_REPO+d.version.name+"/TMP/"+oPms.slug+"/"
        bash=bash+"/bin/mkdir -p "+PATH_TMP+d.name+"/PKGS\n"
        txt=txt+"\n    REPOSITORY: "+d.name+"\n"
        for p in d.packages.all(): 
            bash=bash+"ln -s "+PATH_STORES+p.store.name+"/"+p.name+" "+PATH_TMP+d.name+"/PKGS\n"

        # We create the metadata of repository
        cad=oPms.createrepo

        bash=bash+cad.replace("%REPONAME%",d.name).replace("%PATH%",PATH_TMP[:-1])+"\n"        
        txt=txt+history(d)



    PATH_TMP=PATH_REPO+_version.name+"/TMP/"
    bash=bash+"cp -rf "+PATH_TMP+"* "+PATH_REPO+_version.name+"\n"
    bash=bash+"rm -rf "+PATH_TMP+"\n"

    txt_err=RunInServer(bash)["err"]
    if not txt_err=="":
        txt=txt+"\n\n****ERROR*****\n"+txt_err

    return txt




def RunInServer(code_bash):
    FILE=os.tmpnam() 
    destination = open(FILE, 'wb+')
    destination.write(code_bash)
    destination.close()
    os.system("bash "+FILE+" 1>"+FILE+".out 2>"+FILE+".err")
    destination1 = open(FILE+".out",'rb+')
    out=destination1.read()
    destination1.close()
    destination2 = open(FILE+".err",'rb+')
    err=destination2.read()
    destination2.close()
    os.system("rm "+FILE)
    os.system("rm "+FILE+".out")
    os.system("rm "+FILE+".err")
    return {"out": out,"err": err}

