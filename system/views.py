# -*- encoding: utf-8 -*-
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.shortcuts import render_to_response

from django.http import HttpResponse
from django.http import HttpResponseRedirect
import datetime
from django.db import connection, transaction
import os
import sys

from migasfree.system.models import User
from migasfree.system.models import Computer
from migasfree.system.models import Variable
from migasfree.system.models import Version
from migasfree.system.models import Store
from migasfree.system.models import UserProfile
from migasfree.system.models import Error
from migasfree.system.models import Property
from migasfree.system.models import Fault
from migasfree.system.models import FaultDef
from migasfree.system.models import Query
from migasfree.system.models import Device
from migasfree.system.models import DeviceManufacturer
from migasfree.system.models import DeviceModel
from migasfree.system.models import DeviceConnection
from migasfree.system.models import DeviceType
from migasfree.system.models import Checking

from migasfree.system.logic import *

from django.forms.models import modelformset_factory


from IPy import IP
from django.shortcuts import get_object_or_404
import codecs


from migasfree.system.models import Package
from migasfree.system.models import Repository

from django import forms
from django.forms import ModelForm
from django.db import models

import pickle

#html=""

from django import http

def UserVersion(user):
    try:
        userprofile=UserProfile.objects.get(id=user.id)
        return Version.objects.get(id=userprofile.version_id)
    except:
        return None

#try:
#    MEDIA=getVariable("MEDIA")
#except: #Si no esta el registro lo añadimos
#    oVariable=Variable()
#    oVariable.name="MEDIA"
#    oVariable.value="/srv/www/htdocs/media/"
#    oVariable.save()


# Devuelve el script a ejecutar en la maquina cliente 
def update(request,param):

    def creaxml(properties,faults):
        ret='<?xml version="1.0" encoding="UTF-8" standalone= "yes"?>'+"\n"
        ret=ret+"<MIGASFREE>"

        ret=ret+"<COMPUTER>"
        ret=ret+"<HOSTNAME>$HOSTNAME</HOSTNAME>"
        ret=ret+"<IP>`getip | awk 'BEGIN {FS=\"/\"}; {print $1}'`</IP>"
        ret=ret+"<VERSION>$MIGASFREE_VERSION</VERSION>"
        ret=ret+"<USER>$_USER_GRAPHIC</USER>"
        ret=ret+"<USER_FULLNAME>$_USER_FULLNAME</USER_FULLNAME>"
        ret=ret+"</COMPUTER>"

        ret=ret+"<ATTRIBUTES>"
        for e in properties:
            ret=ret+"<"+e.prefix+">"
            ret=ret+"`"+e.namefunction()+"`"
            ret=ret+"</"+e.prefix+">"
        ret=ret+"</ATTRIBUTES>"

        ret=ret+"<FAULTS>"
        for e in faults:
            ret=ret+"<"+e.name+">"
            ret=ret+"`"+e.namefunction()+"`"
            ret=ret+"</"+e.name+">"
        ret=ret+"</FAULTS>"



        ret=ret+"</MIGASFREE>"
        return ret        



    ret="#!/bin/bash\n\n"
    ret=ret+". /usr/share/migasfree/init\n\n"

    ret=ret+"_USER_FULLNAME=`cat /etc/passwd|grep $_USER_GRAPHIC|cut -d: -f5|cut -d, -f 1`\n\n"

    ret=ret+"# Entities Functions\n\n"
    properties = Property.objects.filter(active=True)
    for e in properties:
        ret=ret + "function "+ e.namefunction() +" {\n"
	ret=ret + e.function.replace("\r","\n") +"\n"
        ret=ret+"}\n"
    ret=ret+"\n"

    ret=ret+"# Faults Functions\n\n"
    faults = FaultDef.objects.filter(active=True)
    for e in faults:
        ret=ret + "function "+ e.namefunction() +" {\n"
	ret=ret + e.function.replace("\r","\n") +"\n"
        ret=ret+"}\n"
    ret=ret+"\n"


    ret=ret+"# Create the file update.xml\n"
    ret=ret+"_FILE_XML=\"$_DIR_TMP/update.xml\"\n"
    ret=ret+"cat > $_FILE_XML << EOF\n"
    ret=ret+creaxml(properties,faults)+"\n"
    ret=ret+"EOF\n\n"

    ret=ret+"# Upload an run update.xml\n"
    ret=ret+"directupload_and_run_response $_FILE_XML \n\n"

    return HttpResponse(ret,mimetype='text/plain')






# ejemplo para subir archivos:
# curl -b PC=$HOSTNAME -F file=@$FILE_YUM_LOG http://127.0.0.1:8000/directupload/ > $FILE_RESP
def directupload(request,self):
    """
    Saves the file directly from the request object.
    Disclaimer:  This is code is just an example, and should
    not be used on a real website.  It does not validate
    file uploaded:  it could be used to execute an
    arbitrary script on the server.
    """
    MEDIA=getVariable("MEDIA")
    def handle_uploaded_file(f,pc):
        import time
        from datetime import datetime

        t=time.strftime("%Y-%m-%d")
        m=time.strftime("%Y-%m-%d %H:%M:%S")

        def grabar():
            destination = open(MEDIA+pc+"."+f.name, 'wb+')
            for chunk in f.chunks():
               destination.write(chunk)
            destination.close()

        ret=f.name+": no permited upload this file in migasfree.system.views.directupload."


        #SI RECIBIMOS UN FICHERO update.xml
        if f.name == "update.xml":
            file=MEDIA+pc+"."+f.name
            grabar()
            destination = open(file, 'rb')
            ret=process_attributes(request,file)             
            os.remove(file)
            destination.close()
            

        #SI RECIBIMOS UN FICHERO history_sw.log
        if f.name == "history_sw.log":
            grabar()
            destination = open(MEDIA+pc+"."+f.name, 'rb')

            try:
                oComputer=Computer.objects.get(name=pc)
            except: #si no esta el Equipo lo añadimos
                oComputer=Computer(name=pc)
                oComputer.alta=t

            oComputer.history_sw=str(oComputer.history_sw)+unicode(destination.read(),"utf-8")
            oComputer.save()
            ret="OK"
            os.remove(MEDIA+pc+"."+f.name)
            destination.close()


        #SI RECIBIMOS UN FICHERO software.log
        if f.name == "software.log":
            grabar()
            destination = open(MEDIA+pc+"."+f.name, 'rb')

            try:
                oComputer=Computer.objects.get(name=pc)
            except: #si no esta el Equipo lo añadimos
                oComputer=Computer(name=pc)
                oComputer.alta=t

            oComputer.software=unicode(destination.read(),"utf-8")
            oComputer.save()
            ret="OK"
            os.remove(MEDIA+pc+"."+f.name)
            destination.close()

        #SI RECIBIMOS UN FICHERO base.log
        if f.name == "base.log":
            grabar()
            destination = open(MEDIA+pc+"."+f.name, 'rb')

            try:
                oVersion=Version.objects.get(name=Computer.objects.get(name=pc).version)
            except: #si no esta el Equipo lo añadimos
                pass
            oVersion.base=unicode(destination.read(),"utf-8")
            oVersion.save()
            ret="OK"
            os.remove(MEDIA+pc+"."+f.name)
            destination.close()

        #SI RECIBIMOS UN FICHERO DIST.ERR
        if f.name == "migasfree.err":
            grabar()
            destination = open(MEDIA+pc+"."+f.name, 'rb')
            try:
                oComputer=Computer.objects.get(name=pc)
            except: #si no esta el Equipo lo añadimos
                oComputer=Computer(name=pc)
                oComputer.dateinput=t
                oComputer.save()

            oError=Error()
            oError.computer=oComputer
            oError.date=m
            oError.error=unicode(destination.read(),"utf-8")
            oError.save()
            ret="OK"
            os.remove(MEDIA+pc+"."+f.name)
            destination.close()



        #SI RECICIMOS UN FICHERO hardware.xml (Inventario Hardware)
        if f.name == "hardware.xml":
            grabar()
#            oResumen=resumenHardware() 

            import codecs
            destination = codecs.open( MEDIA+pc+"."+f.name, "r", "utf-8" )
#            destination = open(MEDIA+pc+"."+f.name,'rb') 
#            oResumen=pickle.load(destination)
            try:
                oComputer=Computer.objects.get(name=pc)
            except: #si no esta el Equipo lo añadimos
                oComputer=Computer(name=pc)
                oComputer.dateinput=t

#            oComputer.mac=oResumen.mac
#            oComputer.cpu=oResumen.cpu
#            oComputer.hd=oResumen.hd
#            oComputer.memoria=oResumen.memoria
#            oComputer.so=oResumen.so
#            oComputer.inventario=oResumen.inventario
#            oComputer.dateupdated=t

            oComputer.hardware=destination.read()
            oComputer.save()
            ret="OK"
            os.remove(MEDIA+pc+"."+f.name)
            destination.close()


        #SI RECICIMOS UN FICHERO install-device (Codigo de instalación de device)
        if f.name == "install_device_code":
            grabar()
            destination = open(MEDIA+pc+"."+f.name, 'rb') 
            oDevice=Device()
            oDevice.name=request.COOKIES.get('NUMBER')

            oDevice.model=DeviceModel.objects.get(name=request.COOKIES.get('MODEL'),devicetype__name=request.COOKIES.get('TYPE'))
            oDevice.connection=DeviceConnection.objects.get(name=request.COOKIES.get('PORT'),devicetype__name=request.COOKIES.get('TYPE'))
            oDevice.values=unicode(destination.read(),"utf-8")
            oDevice.save()
            ret="OK"
            os.remove(MEDIA+pc+"."+f.name)
            destination.close()


        return ret


    if request.method == 'POST':
            # Other data on the request.FILES dictionary:
            #   filesize = len(file['content'])  
            #   filetype = file['content-type']
            ret=handle_uploaded_file(request.FILES['file'],request.COOKIES.get('PC'))
            return HttpResponse(ret,mimetype='text/plain')
    else:
            return HttpResponse("ERROR",mimetype='text/plain')







@login_required
def createrepositories(request,self): # Create the files of Repositories in the server
    version=UserVersion(request.user)
    html=CreateRepositories(version.id)
    return render_to_response("info.html",{"title": "Create Repository Files.","contentpage": html,"user":request.user,"root_path":"/migasfree/admin/"})



def createrepositoriesofpackage(request,self):
    if request.method == 'GET':
            username = request.GET.get('username')
            print username
            password = request.GET.get('password')
            print password
            user = auth.authenticate(username=username, password=password)
            if user is None:
                return HttpResponse("ERROR. User no authenticaded.",mimetype='text/plain')

            if not user.has_perm("system.can_save_package"):
                return HttpResponse("ERROR.  User no have permission for save package. The user must be in the group 'Packager'",mimetype='text/plain')

            ret="OK"            

            CreateRepositoriesofPackage(request.GET.get('PACKAGE'),request.GET.get('VER'))

            return HttpResponse(ret,mimetype='text/plain')
    else:
            return HttpResponse("ERROR",mimetype='text/plain')




def uploadPackage(request,self):
    def handle_uploaded_file(f,store,version,nopkg):

        def grabar():
            import os
            destination = open(PATH_REPO+version+"/STORES/"+store+"/"+f.name, 'wb+')
            for chunk in f.chunks():
               destination.write(chunk)
            destination.close()


        ret=""
        PATH_REPO=getVariable("PATH_REPO")
        try:        
            oVersion=Version.objects.get(name=version)
        except:
            return "No found the version:"+version


        #we add the store
        try: 
            oStore=Store.objects.get(name=store,version=oVersion)
        except: #if not exists the Store, we add it
            oStore=Store()
            oStore.name=store
            oStore.version=oVersion
            oStore.save()

        grabar()

        
        #we add the package
        if nopkg<>"1":
            try:
                oPackage=Package.objects.get(name=f.name,version=oVersion)
            except:
                oPackage=Package(name=f.name,version=oVersion)
            oPackage.store=oStore
            oPackage.save()

        ret="OK"
        return ret 

    if request.method == 'POST':
            # Other data on the request.FILES dictionary:
            #   filesize = len(file['content'])  
            #   filetype = file['content-type']

            username = request.COOKIES.get('username')
            print username
            password = request.COOKIES.get('password')
            print password
            user = auth.authenticate(username=username, password=password)
            if user is None:
                return HttpResponse("ERROR. User no authenticaded.",mimetype='text/plain')

            if not user.has_perm("system.can_save_package"):
                return HttpResponse("ERROR.  User no have permission for save package. The user must be in the group 'Packager'",mimetype='text/plain')

            ret=handle_uploaded_file(request.FILES['file'],request.COOKIES.get('STORE'),request.COOKIES.get('VER'),request.COOKIES.get('NOPKG'))
            return HttpResponse(ret,mimetype='text/plain')
    else:
            return HttpResponse("ERROR",mimetype='text/plain')


def uploadSet(request,self):
    def handle_uploaded_file(f,store,version,packageset):

        def grabar():
            import os
            destination = open(PATH_REPO+version+"/STORES/"+store+"/"+packageset+"/"+f.name, 'wb+')
            for chunk in f.chunks():
               destination.write(chunk)
            destination.close()






        ret=""
        PATH_REPO=getVariable("PATH_REPO")
        try:        
            oVersion=Version.objects.get(name=version)
        except:
            return "No found the version:"+version


        #we add the store
        try: 
            oStore=Store.objects.get(name=store,version=oVersion)
        except: #if not exists the Store, we add it
            oStore=Store()
            oStore.name=store
            oStore.version=oVersion
            oStore.save()

        #we add the Package/Set
        try:
            oPackage=Package.objects.get(name=packageset,version=oVersion)
        except:
            oPackage=Package(name=packageset,version=oVersion)
        oPackage.store=oStore
        oPackage.save()
        oPackage.create_dir()

        grabar()

        ret="OK"
        return ret 

    if request.method == 'POST':
            # Other data on the request.FILES dictionary:
            #   filesize = len(file['content'])  
            #   filetype = file['content-type']

            username = request.COOKIES.get('username')
            password = request.COOKIES.get('password')
            user = auth.authenticate(username=username, password=password)
            if user is None:
                return HttpResponse("ERROR. User no authenticaded.",mimetype='text/plain')

            if not user.has_perm("system.can_save_package"):
                return HttpResponse("ERROR.  User no have permission for save package. The user must be in the group 'Packager'",mimetype='text/plain')    

            ret=handle_uploaded_file(request.FILES['file'],request.COOKIES.get('STORE'),request.COOKIES.get('VER'),request.COOKIES.get('SET'))
            return HttpResponse(ret,mimetype='text/plain')
    else:
            return HttpResponse("ERROR",mimetype='text/plain')



    


def option_description(campo,value):
    try:
        return campo.split('<option value="'+value+'">')[1].split("</option>")[0]
    except:
        return value


def query2(request,parameters,FormParam):

    from django.db.models import Q
    from django.template import Context, Template

    oQuery=Query.objects.get(id=parameters["id_query"])
  
    #VARIABLES 
    VERSION=parameters["user_version"]

    #EJECUTAMOS LA CONSULTA
    try:
        exec(oQuery.code.replace("\r",""))


        if vars().has_key("fields")==False:
            fields=[]
            for k,v in query.values()[0].iteritems():
                fields.append(k)

        if vars().has_key("titles")==False:
            titles=fields

    
        vl_fields=query.values().values_list(*fields)

        filters=[]
        for x in FormParam:
            if not (x.name=="id_query" or x.name=="user_version"):
               filters.append(str(x.label)+": "+parameters[x.name+"_display"])
                
               

        return HttpResponse(render_to_response('query.html', Context({"title": oQuery.name,"description": oQuery.description, "titles": titles,"query":vl_fields,"filters":filters,"user":request.user,"root_path":"/migasfree/admin/"})),mimetype='text/html;charset=utf-8')
    except:

        return HttpResponse("Error in field 'code' of query:\n"+str(sys.exc_info()),mimetype="text/plain")











@login_required
def query(request,param):
    from migasfree.system.forms import ParametersForm
    from django.forms import ChoiceField

    if request.method == 'POST': # Si el formulario de parametros ha sido enviado: 
        parameters={}
        for p in request.POST:
            parameters[p]=request.POST.get(p)


        oQuery=Query.objects.get(id=request.POST.get('id_query',''))
        dic_initial={'id_query': request.POST.get('id_query',''),'user_version': UserVersion(request.user).id}
        if oQuery.parameters == "" :
            return query2(request,dic_initial)
        else:
            try:
                exec(oQuery.parameters.replace("\r",""))
                g_FormParam=formParams()(initial=dic_initial)
                
                for x in g_FormParam:
                    parameters[x.name+"_display"] = option_description(str(x),parameters[x.name])
       
                return query2(request,parameters,g_FormParam)
  
            except:      

                return HttpResponse("Error in field 'parameters' of query:\n"+ str(sys.exc_info()[1]),mimetype="text/plain")



    else: # Se muestra el formulario de parametros
        oQuery=Query.objects.get(id=request.GET.get('id',''))
        dic_initial={'id_query': request.GET.get('id',''),'user_version': UserVersion(request.user).id}
        if oQuery.parameters == "" :
            return query2(request,dic_initial,{})
        else:

 
            try:
                exec(oQuery.parameters.replace("\r",""))
                g_FormParam=formParams()(initial=dic_initial)
            
                return render_to_response('parameters.html', {'form': g_FormParam, 'title': _("Parameters for Query:") +" "+ oQuery.name,"user":request.user,"root_path":"/migasfree/admin/" })
            except:
                return HttpResponse("Error in field 'parameters' of query:\n"+ str(sys.exc_info()[1]),mimetype="text/plain")



def device(request,param):

    def selection(title,options):
        
        if (len(options)<=1) and (title=="TYPE" or title=="PORT"):
            ret="_"+title+"=\""+options[0]+"\"\n" 
        else:
            ret="dialog --backtitle \"migasfree - INSTALL DEVICE\" --menu \""+ title +"\" 0 0 0"
            i=0
            for o in options:
                ret=ret+" \""+str(i)+"\" \""+o+"\""
                i=i+1
            ret=ret+" 2>/tmp/ans\n"
            ret=ret+"#CANCEL\n"
            ret=ret+"if [ $? = 1 ]\n then\n"
            ret=ret+"   rm -f /tmp/ans\n"
            ret=ret+"   clear\n"
            ret=ret+"   exit 0\n"
            ret=ret+"fi\n"
            ret=ret+"_OPCION=\"`cat /tmp/ans`\"\n"
            ret=ret+"clear\n"
            i=0
            for o in options:
                ret=ret+"if [ $_OPCION = \""+str(i)+"\" ] \n  then\n"
                ret=ret+"_"+title+"=\""+o+"\"\n"
                ret=ret+"fi\n"
                i=i+1
        return ret

    def listType():
        l=[]
        types=DeviceType.objects.all()
        for o in types:
            l.append(o.name)
        return l

    def listManufacturer(devicetype):
        l=[]
        manufacturers=DeviceManufacturer.objects.filter(devicemodel__devicetype__name=devicetype).distinct()
        for o in manufacturers:
            l.append(o.name)
        return l

    def listModel(devicetype,manufacturer):
        l=[]
        models=DeviceModel.objects.filter(devicetype__name=devicetype,manufacturer__name=manufacturer)
        for o in models:
            l.append(o.name)
        return l

    def listPort(model):
        l=[]
        connections=DeviceConnection.objects.filter(devicemodel__name=model)
        for o in connections:
            l.append(o.name)
        return l

    def whatdevicetype(number):
        ret="#!/bin/bash\n" 
        ret=ret+"#whatmodel\n"
        ret=ret+". /usr/share/migasfree/init\n"
        ret=ret+"_FILE_MIGAS=/tmp/install_device_type\n"
        ret=ret+"chmod 700 $_FILE_MIGAS\n"
        ret=ret+"_NUMBER="+number+"\n"
        ret=ret+selection("TYPE", listType() )
        ret=ret+"download_file \"device/?CMD=install&HOST=$HOSTNAME&TYPE=$_TYPE&NUMBER=$_NUMBER\" \"$_FILE_MIGAS\"\n" 

        ret=ret+"if [ $? == 0 ]\n  then\n"
        ret=ret+"   chmod 700 $_FILE_MIGAS\n"
        ret=ret+"   $_FILE_MIGAS\n"
        ret=ret+"fi\n"
        return ret

    def whatdevicemanufacturer(number,devicetype):
        ret="#!/bin/bash\n" 
        ret=ret+"#whatmanufacturer\n"
        ret=ret+". /usr/share/migasfree/init\n"
        ret=ret+"_FILE_MIGAS=/tmp/install_device_manufacturer\n"
        ret=ret+"chmod 700 $_FILE_MIGAS\n"
        ret=ret+"_NUMBER="+number+"\n"
        ret=ret+"_TYPE="+devicetype+"\n"
        ret=ret+selection("MANUFACTURER", listManufacturer(devicetype) )
        ret=ret+"download_file \"device/?CMD=install&HOST=$HOSTNAME&MANUFACTURER=$_MANUFACTURER&TYPE=$_TYPE&NUMBER=$_NUMBER\"  \"$_FILE_MIGAS\"\n"

        ret=ret+"if [ $? == 0 ]\n  then\n"
        ret=ret+"   chmod 700 $_FILE_MIGAS\n"
        ret=ret+"   $_FILE_MIGAS\n"
        ret=ret+"fi\n"
        return ret



    def whatmodel(number,devicetype,manufacturer):
        ret="#!/bin/bash\n" 
        ret=ret+"#whatmodel\n"
        ret=ret+". /usr/share/migasfree/init\n"
        ret=ret+"_FILE_MIGAS=/tmp/install_device_model\n"
        ret=ret+"chmod 700 $_FILE_MIGAS\n"
        ret=ret+"_NUMBER="+number+"\n"
        ret=ret+"_TYPE="+devicetype+"\n" 
        ret=ret+"_MANUFACTURER="+manufacturer+"\n"
        ret=ret+selection("MODEL", listModel(devicetype,manufacturer) )
        ret=ret+"download_file \"device/?CMD=install&HOST=$HOSTNAME&MODEL=$_MODEL&MANUFACTURER=$_MANUFACTURER&TYPE=$_TYPE&NUMBER=$_NUMBER\" \"$_FILE_MIGAS\"\n"

        ret=ret+"if [ $? == 0 ]\n  then\n"
        ret=ret+"   chmod 700 $_FILE_MIGAS\n"
        ret=ret+"   $_FILE_MIGAS\n"
        ret=ret+"fi\n"
        return ret

    def whatport(number,devicetype,manufacturer,model):
        ret="#!/bin/bash\n" 
        ret=ret+"#whatport\n"
        ret=ret+". /usr/share/migasfree/init\n"
        ret=ret+"_FILE_MIGAS=/tmp/install_device_port\n"
        ret=ret+"chmod 700 $_FILE_MIGAS\n"
        ret=ret+"_NUMBER="+number+"\n"
        ret=ret+"_TYPE="+devicetype+"\n"
        ret=ret+"_MANUFACTURER="+manufacturer+"\n"
        ret=ret+"_MODEL="+model+"\n"
        ret=ret+selection("PORT",listPort(model))
        ret=ret+"download_file \"device/?CMD=install&HOST=$HOSTNAME&MODEL=$_MODEL&MANUFACTURER=$_MANUFACTURER&TYPE=$_TYPE&NUMBER=$_NUMBER&PORT=$_PORT\" \"$_FILE_MIGAS\"\n"


        ret=ret+"if [ $? == 0 ]\n then\n"
        ret=ret+"   chmod 700 $_FILE_MIGAS\n"
        ret=ret+"   $_FILE_MIGAS\n"
        ret=ret+"fi\n"
        return ret

    def processmodel(number,devicetype,manufacturer,model,port):
        ret="#!/bin/bash\n"
        ret=ret+". /usr/share/migasfree/init\n"
        ret=ret+"_FILE_MIGAS=/tmp/install_device_code\n"
        ret=ret+"_FILE_RESP=/tmp/resp\n"
        oDeviceModel=DeviceModel.objects.get(name=model)
        oDeviceConnection=DeviceConnection.objects.get(name=port,devicetype__name=devicetype)

        precode=oDeviceModel.precode.replace("$_MODEL",model).replace("$_FILE",oDeviceModel.filename)+"\n"
        code=oDeviceConnection.code.replace("$_MODEL",model).replace("$_FILE",oDeviceModel.filename)+"\n"
        postcode=oDeviceModel.postcode.replace("$_MODEL",model).replace("$_FILE",oDeviceModel.filename)+"\n"

        fields=oDeviceConnection.fields.split()
        for f in fields:
            ret=ret+"dialog --backtitle \"migasfree - INSTALL DEVICE\" --inputbox \""+f+"\" 0 0 2>/tmp/ans\n"
            ret=ret+"#CANCEL\n"
            ret=ret+"if [ $? = 1 ]\n  then\n"
            ret=ret+"  rm -f /tmp/ans\n"
            ret=ret+"  clear\n"
            ret=ret+"  exit 0\n"
            ret=ret+"fi\n"
            ret=ret+"_"+f+"=`cat /tmp/ans`\n"  

        ret=ret+"clear\n"     
        ret=ret+"echo \"Install Device:\n"+precode+code+postcode+"\"\n"

        ret=ret+precode+"\n"
        ret=ret+"if [ $? -ne 0 ]\n then\n"
        ret=ret+"  echo ERROR\n"
        ret=ret+"  exit 0\n" 
        ret=ret+"fi\n"
        ret=ret+code+"\n"
        ret=ret+"if [ $? -ne 0 ]\n  then\n"
        ret=ret+"  echo ERROR\n"
        ret=ret+"  exit 0\n" 
        ret=ret+"fi\n"
        ret=ret+postcode+"\n"
        ret=ret+"if [ $? -ne 0 ]\n  then\n"
        ret=ret+"  echo ERROR\n"
        ret=ret+"  exit 0\n" 
        ret=ret+"fi\n"

        ret=ret+"cat > $_FILE_MIGAS << EOF \n"
        ret=ret+precode+code+postcode
        ret=ret+"EOF\n"


        #We add the device
        ret=ret+"upload_file \"$_FILE_MIGAS\" directupload/ \"PC=$HOSTNAME;TYPE="+devicetype+";NUMBER="+number+";MODEL="+model+";PORT="+port+"\"\n"


        return ret



    host=request.GET.get('HOST','')
    number=request.GET.get('NUMBER','')
    devicetype=request.GET.get('TYPE','')
    manufacturer=request.GET.get('MANUFACTURER','')
    model=request.GET.get('MODEL','')
    port=request.GET.get('PORT','')
    cmd=request.GET.get('CMD','')

    if cmd=="install":
        if port=="":
            cursor=Device.objects.filter(name=number)
        else:
            cursor=Device.objects.filter(name=number,connection__name=port)
            if len(cursor)==1:
                return HttpResponse(cursor[0].values,mimetype="text/plain")

        if len(cursor)>0 : # Si se ha configurado alguna vez el dispositivo
            model=cursor[0].model.name      
            if len(DeviceConnection.objects.filter(devicemodel__name=model))==1 : #SI el modelo tiene 1 conexion
                return HttpResponse(cursor[0].values,mimetype="text/plain")
            else: #SI el modelo no tiene 1 conexion
                if port=="":
                    ret=whatport(number,DeviceModel.objects.get(name=model).devicetype.name,DeviceModel.objects.get(name=model).manufacturer.name,model)
                    return HttpResponse(ret,mimetype="text/plain")
                else:
                    #Existe un device con este port ya configurado?
                    cursor=cursor.filter(connection__name=port)
                    if len(cursor)==1:
                        return HttpResponse(cursor[0].values,mimetype="text/plain")
                    else:                    
                        ret=processmodel(number,DeviceModel.objects.get(name=model).devicetype.name,DeviceModel.objects.get(name=model).manufacturer.name,model,port)
                        return HttpResponse(ret,mimetype="text/plain")

        else: #si no está el Device lo añadimos
            # Pedimos el device type
            if devicetype == "" :        
                ret=whatdevicetype(number)
                return HttpResponse(ret,mimetype="text/plain")

            # Pedimos el fabricante
            if manufacturer == "" :        
                ret=whatdevicemanufacturer(number,devicetype)
                return HttpResponse(ret,mimetype="text/plain")

            # Pedimos el modelo
            if model == "" :        
                ret=whatmodel(number,devicetype,manufacturer)
                return HttpResponse(ret,mimetype="text/plain")
     
            # Pedimos el puerto
            if port == "" :
                ret=whatport(number,devicetype,manufacturer,model)
                return HttpResponse(ret,mimetype="text/plain")
        
            else:
                #Devolvemos el script para la instalacion
                ret=processmodel(number,devicetype,manufacturer,model,port)
                return HttpResponse(ret,mimetype="text/plain")



        

@login_required
def info(request,param):
    from django.template import Context, Template

    from django.shortcuts import render_to_response

    version=UserVersion(request.user)
    PATH=getVariable("PATH_REPO")+version.name+"/"
    RUTA=PATH+param   

    try:
        elements=os.listdir(RUTA)
    except:
        # GET INFORMATION OF PACKAGE
        cad="echo \"VERSION: "+version.name+"\"\n"
        cad=cad+"echo \"PACKAGE: "+param[:-1]+"\"\n"
        cad=cad+"echo \n"
        cad=cad+"echo \n"
        cad=cad+"PACKAGE="+RUTA[:-1]+"\n"
        cad=cad+version.pms.info
        ret=RunInServer(cad)["out"]
        return render_to_response("info-package.html",{"title": "Information of Package.","contentpage": ret,"user":request.user,"root_path":"/migasfree/admin/"})

    # NAVIGATION FOR FOLDERS
    vl_fields=[]
    filters=[]
    titles=[]
    filters.append(param)
    if param>"/":
        vl_fields.append(["folder.png",".."])

    for e in elements:
        try:
            if (os.stat(RUTA+e).st_mode<32000): #TODO: asegurarse de que esto sirve para identificar si es un archivo o un directorio
                vl_fields.append(["folder.png",e+"/"])
            else:
                vl_fields.append(["package.png",e+"/"])
        except:
            pass

    return render_to_response('info-folder.html', Context({"title": "Information of Package.","description": "VERSION: "+version.name,"filters":filters, "query":vl_fields,"user":request.user,"root_path":"/migasfree/admin/"}))



def login(request,param):
    from django.template import Context, Template
    if request.method == 'GET':
        return render_to_response('admin/login.html',Context({"user":request.user,"root_path":"/migasfree/admin/"}))
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            # Correct password, and the user is marked "active"
            auth.login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect("/migasfree/main/")
        else:
            # Show the login page
            return HttpResponseRedirect("/migasfree/login/")


def main(request,param):
    """
    Main Menu of migasfree 
    """
    from django.template import Context, Template


    if not request.user.is_authenticated():
            return HttpResponseRedirect('/migasfree/login')

    version=UserVersion(request.user)
    status=[]
    filters=[]
    titles=[]
    filters.append(param)


    for obj in Checking.objects.filter(active=True):

        try:
            exec(obj.code.replace("/r",""))
            if vars().has_key("result")==True:
                result=vars()["result"]
                if result<>0:

                    if vars().has_key("message")==False:
                        message=_(obj.name)
                    else:
                        message=_(vars()["message"])

                    if vars().has_key("url")==False:
                        url="/migasfree/main"                        
                    else:
                        url=vars()["url"]


                    if vars().has_key("icon")==False:
                        icon="information.png"
                    else:
                        icon=vars()["icon"]


                    status.append([icon,[url,str(result)+" "+message]])

        except:
            return HttpResponse("Error in field 'code' of Checking:"+obj.message+"\n"+str(sys.exc_info()),mimetype="text/plain")  





    if len(status)==0:
        status.append(["checking.png", ["",_("All O.K.")]])

    return HttpResponse(render_to_response('main.html', Context({"title": _("Main Menu"),"description": "","filters":filters, "status":status,"user":request.user,"root_path":"/migasfree/admin/","LANGUAGE_CODE": request.LANGUAGE_CODE})),mimetype='text/html;charset=utf-8')




def system(request,param):
    """
    System Menu of migasfree 
    """
    from django.template import Context, Template


    if not request.user.is_authenticated():
            return HttpResponseRedirect('/migasfree/login')

    version=UserVersion(request.user)
    status=[]
    filters=[]
    titles=[]
    filters.append(param)

    return HttpResponse(render_to_response('system.html', Context({"title": _("System Menu"),"description": "","filters":filters, "status":status,"user":request.user,"root_path":"/migasfree/admin/","LANGUAGE_CODE": request.LANGUAGE_CODE})),mimetype='text/html;charset=utf-8')


LastUrl=""
@login_required()
def changeVersion(request,param):

    def formParamsVersion():
        from migasfree.system.forms import ParametersForm
        class myForm(ParametersForm):
            version=forms.ModelChoiceField(Version.objects.all())
        return myForm

    if request.method == 'POST': # Si el formulario de parametros ha sido enviado: 
        parameters={}
        for p in request.POST:
            parameters[p]=request.POST.get(p)
        oUserProfile=UserProfile.objects.get(id=request.user.id)
        oUserProfile.version=Version.objects.get(id=parameters["version"])
        oUserProfile.save()
        return HttpResponseRedirect(request.session["LastUrl"])

    else:
        dic_initial={'user_version': UserVersion(request.user).id,"root_path":"/migasfree/admin",'version': UserVersion(request.user).id}
        g_FormParam=formParamsVersion()(initial=dic_initial)
        try:
            request.session["LastUrl"]= request.META["HTTP_REFERER"]
        except:
            request.session["LastUrl"]="/migasfree/main"
        return render_to_response('parameters.html', {'form': g_FormParam, 'title': _("Change version for")+" "+ request.user.username,"user":request.user,"root_path":"/migasfree/admin/"})
  
  
def softwarebase(request,param):
    VERSION=request.GET.get('VERSION','')
    try:
        ret=Version.objects.get(name=VERSION).base
    except:
        ret=""
    return HttpResponse(ret,mimetype="text/plain")




def documentation(request,param):
    """
    Manuals Page 
    """
    from django.template import Context, Template


    if not request.user.is_authenticated():
            return HttpResponseRedirect('/migasfree/login')

    version=UserVersion(request.user)
    filters=[]
    titles=[]
    filters.append(param)

    return HttpResponse(render_to_response('documentation.html', Context({"title": _("Documentation"),"description": "","filters":filters, "user":request.user,"root_path":"/migasfree/admin/","LANGUAGE_CODE": request.LANGUAGE_CODE})),mimetype='text/html;charset=utf-8')

