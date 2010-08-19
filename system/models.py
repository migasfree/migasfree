# -*- encoding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _


from django.db import models
from django.db import connection, transaction
import os
import time
from django import forms

from django.forms import ModelForm
from migasfree.middleware import threadlocals

from django.contrib.auth.models import User as UserSystem
from django.contrib.auth.models import UserManager

from django.db.models import F
from django.db.models.signals import m2m_changed


# Return the user version that logged.
def UserVersion():
    try:
        return UserProfile.objects.get(id=threadlocals.get_current_user().id).version
    except:
        return None

# VersionManager is used for filter the property "objects" of somethings class by the version of user logged.
class VersionManager(models.Manager):
    def get_query_set(self):
        user_version=UserVersion()
        if user_version==None:
            return self.version(0)
        else:
            return self.version(user_version)

    def version(self,VERSION):
        if VERSION==0: # return the objects of ALL VERSIONS 
            return super(VersionManager,self).get_query_set()
        else: # return only the objects of this VERSION
            return super(VersionManager,self).get_query_set().filter(version=VERSION)



class Variable(models.Model):
    name = models.CharField(_("name"),max_length=50,null=True, blank=True, unique=True)
    value= models.CharField(_("value"),max_length=250,null=True, blank=True)
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Variable")
        verbose_name_plural = _("Variables")
        permissions = (("can_save_variable", "Can save Variable"),)



class Pms(models.Model):
    """Package Management System

    Each distribution of linux have a P.M.S. For example Fedora uses yum, Ubuntu uses apt, openSUSE zypper, etc.

    For default migasfree is configurate for work whith apt, yum and zypper.

    This model is used for say to migasfree server how must:
        - create the metadata of the repositories in the server. 
        - define the source list file of repositories for the client. 
        - get info of packages in the server for the view 'Packages Information'.
"""
    name = models.CharField(_("name"),max_length=50,unique=True)
    slug = models.CharField(_("slug"),max_length=50,null=True, blank=True,default="REPOSITORIES")
    createrepo = models.TextField(_("create repository"),null=True, blank=True,help_text=_("Code bash. Define how create the metadata of repositories in the migasfree server."))
    repository = models.TextField(_("repository definition"),null=True, blank=True,help_text=_("Define the content of source list file of repositories for the client."))
    info = models.TextField(_("package information"),null=True, blank=True,help_text=_("Code bash. Define how get info of packages in the server"))
    def __unicode__(self):
        return self.name

    def save(self):
        self.createrepo=self.createrepo.replace("\r\n","\n")
        self.repository=self.repository.replace("\r\n","\n")
        self.info=self.info.replace("\r\n","\n")
        super(Pms, self).save() # Call the "real" save() method

    class Meta:
        verbose_name = _("Package Management System")
        verbose_name_plural = _("Package Management Systems")
        permissions = (("can_save_pms", "Can save Package Management System"),)

class Version(models.Model):
    "Version of S.O. by example 'AZLinux-2'"
    name = models.CharField(_("name"),max_length=50,unique=True)
    pms = models.ForeignKey(Pms,verbose_name=_("package management system"))
    computerbase= models.CharField(_("Computer base"),max_length=50,help_text=_("Name of computer with the software base"))
    base = models.TextField(_("software base"),null=False, blank=True,help_text=_("List ordered of packages base for this version"))  


    def __unicode__(self):
        return self.name

    def create_dirs(self):
        PATH_REPO=Variable.objects.get(name='PATH_REPO').value
        USER_WEB_SERVER=Variable.objects.get(name='USER_WEB_SERVER').value
        os.system("mkdir -p "+PATH_REPO+self.name+"/REPOSITORIES")
        os.system("mkdir -p "+PATH_REPO+self.name+"/STORES")
        os.system("chown -R "+USER_WEB_SERVER+":root "+PATH_REPO+self.name)

    def save(self):
        self.name=self.name.replace(" ","-")
        self.create_dirs()
        self.base=self.base.replace("\r\n","\n")
        super(Version, self).save() # Call the "real" save() method

    def delete(self):
        # remove the directory of this version
        PATH_REPO=Variable.objects.get(name='PATH_REPO').value
        os.system("rm -rf "+PATH_REPO+self.name+"\n")
        super(Version,self).delete() # Call the real delete() method

    class Meta:
        verbose_name = _("Version")
        verbose_name_plural = _("Versions")
        permissions = (("can_save_version", "Can save Version"),)


class Computer(models.Model):
    name = models.CharField(_("name"),max_length=50,null=True, blank=True,unique=True)
    version= models.ForeignKey(Version,verbose_name=_("version"))
    ip=models.CharField(_("ip"),max_length=50,null=True, blank=True)
    mac=models.TextField(_("mac"),null=True, blank=True) 
    dateinput = models.DateField(_("date input"),help_text=_("Date of input of Computer in migasfree system")) 
#    dateupdated = models.DateField(_("date updated"),null=True, blank=True,help_text=_("Date of inventory hardware")) 
    hardware=models.TextField(_("hardware inventory"),null=True, blank=True) 
    history_hw=models.TextField(_("hardware history"),default="",null=True, blank=True) 
    software=models.TextField(_("software inventory"),null=True, blank=True,help_text=_("differences of packages respect the software base of the version"))  
    history_sw=models.TextField(_("software history"),default="",null=True, blank=True) 


    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Computer")
        verbose_name_plural = _("Computers")
        permissions = (("can_save_computer", "Can save Computer"),)



class Error(models.Model):
    computer= models.ForeignKey(Computer,verbose_name=_("computer"))
    date= models.DateTimeField(_("date"),default=0)
    error= models.TextField(_("error"),null=True, blank=True)
    checked = models.BooleanField(_("checked"),default=False,help_text="")

    def autoCheck(self):
        msg=self.error
        for ace in AutoCheckError.objects.all():
            msg=msg.replace(ace.message,"")  
        msg=msg.replace("\n","")
        if msg=="":
            self.checked=True


    def linkComputer(self):
        return '<a href="%s">%s</a>' % ( "../Computer/"+str(self.computer.id), self.computer.name )
    linkComputer.allow_tags=True

    def save(self):
        self.error=self.error.replace("\r\n","\n")
        self.autoCheck()
        super(Error, self).save()

    def __unicode__(self):
        return str(self.id)+" - "+self.computer.name+" - "+ str(self.date)

    class Meta:
        verbose_name = _("Error")
        verbose_name_plural = _("Errors")
        permissions = (("can_save_error", "Can save Error"),)



class User(models.Model):
    "User:"
    name = models.CharField(_("name"),max_length=50,unique=True)
    fullname = models.CharField(_("fullname"),max_length=50)
    def __unicode__(self):
        return self.name+" - "+self.fullname

    class Meta:
        verbose_name = _("User") 
        verbose_name_plural = _("Users")
        permissions = (("can_save_user", "Can save User"),)


class Store(models.Model):
    "Ubicacion: rutas donde se guardaran los paquetes. P.e. /terceros/vmware"
    name = models.CharField(_("name"),max_length=50)
    version= models.ForeignKey(Version,verbose_name=_("version"))
    objects = VersionManager() # manager by user version

    def create_dir(self):
        PATH_REPO=Variable.objects.get(name='PATH_REPO').value
        USER_WEB_SERVER=Variable.objects.get(name='USER_WEB_SERVER').value
        os.system("mkdir -p "+PATH_REPO+self.version.name+"/STORES/"+self.name)
        os.system("chown -R "+USER_WEB_SERVER+":root "+PATH_REPO+self.version.name+"/STORES/"+self.name)

    def save(self):
        self.name=self.name.replace(" ","-")
        self.create_dir()
        super(Store, self).save()

    def delete(self):
        # remove the directory of Store
        PATH_REPO=Variable.objects.get(name='PATH_REPO').value
        os.system("rm -rf "+PATH_REPO+self.version.name+"/STORES/"+self.name)
        super(Store,self).delete() 

    def __unicode__(self):
        return self.name

    class Meta():
        verbose_name = _("Store")
        verbose_name_plural = _("Stores")
        unique_together=(("name","version"),)
        permissions = (("can_save_store", "Can save Store"),)


class Package(models.Model):
    "Package:"
    name = models.CharField(_("name"),max_length=50)
    version= models.ForeignKey(Version,verbose_name=_("version"))
    objects = VersionManager() # manager by user version
    store = models.ForeignKey(Store,verbose_name=_("store"))

    def create_dir(self):
        PATH_REPO=Variable.objects.get(name='PATH_REPO').value
        USER_WEB_SERVER=Variable.objects.get(name='USER_WEB_SERVER').value
        print PATH_REPO+self.version.name+"/STORES/"+self.store.name+"/"+self.name
        os.system("mkdir -p "+PATH_REPO+self.version.name+"/STORES/"+self.store.name+"/"+self.name)
        os.system("chown -R "+USER_WEB_SERVER+":root "+PATH_REPO+self.version.name+"/STORES/"+self.store.name+"/"+self.name)


    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = _("Package/Set")
        verbose_name_plural = _("Packages/Sets")
        unique_together=(("name","version"),)
        permissions = (("can_save_package", "Can save Package"),)


class Property(models.Model):

    KIND_CHOICES = (
    ('N', _('NORMAL')),
    ('-', _('LIST')),
    ('L', _('ADDS LEFT')),
    ('R', _('ADDS RIGHT')),
    )

    prefix = models.CharField(_("prefix"),max_length=3,unique=True)
    name = models.CharField(_("name"),max_length=50)
    function = models.TextField(_("function"),null=True, blank=True, help_text=_("Code bash. This code will execute in the client computer, and it must put in the standard output the value of the attribute correspondent to this property.<br>The format of this value is 'name~description', where 'description' is optional.<br><b>Example of code:</b><br>#Create a attribute with the name of commputer<br> echo $HOSTNAME"))
    before_insert = models.TextField(_("before insert"),null=False, blank=True,help_text=_("Code django. This code will execute before insert the attribute in the server. You can modify the value of attribute here, using the variable 'data'."))
    after_insert = models.TextField(_("after insert"),null=False, blank=True,help_text=_("Code django. This code will execute after insert the attribute in the server."))
    active = models.BooleanField(_("active"),default=True,help_text="")
    kind = models.CharField(_("kind"),max_length=1, default="N", choices=KIND_CHOICES)
    auto=models.BooleanField(_("auto"),default=True,help_text="automatically add the attribute to database")

 
    def namefunction(self):
        return "PROPERTY_"+self.prefix

    def __unicode__(self):
        return self.name

    def save(self):
        self.before_insert=self.before_insert.replace("\r\n","\n")
        self.after_insert=self.after_insert.replace("\r\n","\n")
        super(Property, self).save() # Call the "real" save() method

    class Meta:
        verbose_name = _("Property")
        verbose_name_plural = _("Properties")
        permissions = (("can_save_property", "Can save Property"),)

class Attribute(models.Model):
    property_att = models.ForeignKey(Property,verbose_name=_("Property of attribute"))
    value = models.CharField(_("value"),max_length=250)
    description = models.TextField(_("description"),null=True, blank=True)

    def linkProperty(self):
        return '<a href="%s">%s</a>' % ( "../Property/"+str(self.property_att.id), self.property_att.name )
    linkProperty.allow_tags=True

    def __unicode__(self):
        return self.property_att.prefix+"-"+self.value+" "+self.description
        return self.value+" "+self.description


    class Meta:
        verbose_name = _("Attribute")
        verbose_name_plural = _("Attributes")
        unique_together=(("property_att","value"),)
        permissions = (("can_save_attribute", "Can save Attribute"),)


class FaultDef(models.Model):
    name = models.CharField(_("name"),max_length=50,unique=True)
    description = models.TextField(_("description"),null=True, blank=True)
    function = models.TextField(_("function"),null=True, blank=True)
    active = models.BooleanField(_("active"),default=True)

    def save(self):
        self.name=self.name.replace(" ","_")
        super(FaultDef, self).save()

    def namefunction(self):
        return "FAULT_"+self.name

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Fault Definition")
        verbose_name_plural = _("Faults Definition")
        permissions = (("can_save_faultdef", "Can save Fault Definition"),)

class Fault(models.Model):
    computer= models.ForeignKey(Computer,verbose_name=_("computer"))
    date= models.DateTimeField(_("date"),default=0)
    text= models.TextField(_("text"),null=True, blank=True)
    faultdef = models.ForeignKey(FaultDef,verbose_name=_("fault definition"))
    checked = models.BooleanField(_("checked"),default=False,help_text="")

    def linkComputer(self):
        return '<a href="%s">%s</a>' % ( "../Computer/"+str(self.computer.id), self.computer.name )
    linkComputer.allow_tags=True

    def __unicode__(self):
        return str(self.id)+" - "+self.computer.name+" - "+ str(self.date)

    class Meta:
        verbose_name = _("Fault")
        verbose_name_plural = _("Faults")
        permissions = (("can_save_fault", "Can save Fault"),)



class Schedule(models.Model):
    name = models.CharField(_("name"),max_length=50,null=True, blank=True,unique=True)
    description = models.TextField(_("description"),null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")
        permissions = (("can_save_schedule", "Can save Schedule"),)


       
class ScheduleDelay(models.Model):
    delay = models.IntegerField(_("delay")) 
    schedule = models.ForeignKey(Schedule,verbose_name=_("schedule"))
    attributes = models.ManyToManyField(Attribute,null=True, blank=True,verbose_name=_("attributes"))

    def __unicode__(self):
        return str(self.delay)+" - "+self.schedule.name

    def list_attributes(self):
        cattributes=""
        for i in self.attributes.all():
            cattributes=cattributes+ i.value +","
        return cattributes[0:len(cattributes)-1]
    list_attributes.short_description = _("attributes")

    class Meta:
        verbose_name = _("Schedule Delay")
        verbose_name_plural = _("Schedule Delays")
        unique_together=(("schedule","delay"),)
        permissions = (("can_save_scheduledelay", "Can save Schedule Delay"),)



class Repository(models.Model):
    "Repository:"

    name = models.CharField(_("name"),max_length=50)
    version= models.ForeignKey(Version,verbose_name=_("version"))
    active = models.BooleanField(_("active"),default=True,help_text=_("if you uncheck this field, the repository is hidden for all computers."))
    date = models.DateField(_("date"),help_text=_("Date initial for distribute."))
    comment = models.TextField(_("comment"),null=True, blank=True)
    toinstall = models.TextField(_("packages to install"),null=True, blank=True)
    toremove = models.TextField(_("packages to remove"),null=True, blank=True)
    packages = models.ManyToManyField(Package,null=True, blank=True,verbose_name=_("packages/sets"))
    attributes= models.ManyToManyField(Attribute, null=True, blank=True,verbose_name=_("attributes"))
    objects = VersionManager() # manager by user version
    schedule = models.ForeignKey(Schedule, null=True, blank=True, verbose_name=_("schedule"))

    modified= models.BooleanField(_("modified"),default=False,editable=False) # used to "createrepositories"
    createpackages = models.ManyToManyField(Package,null=True, blank=True,verbose_name=_("createpackages"),related_name="createpackages",editable=False) # used to know when "createrepositories"

    def __unicode__(self):
        return u'%s' % (self.name)

    def save(self):       
        self.name=self.name.replace(" ","_")
        super(Repository, self).save() # Call the "real" save() method



    def delete(self):
        # remove the directory of repository
        PATH_REPO=Variable.objects.get(name='PATH_REPO').value
        os.system("rm -rf "+PATH_REPO+self.version.name+"/"+self.version.pms.slug+"/"+self.name+"\n")
        super(Repository,self).delete() # Call the real delete() method

    def timeline(self):
        from system.logic import horizon
        from datetime import datetime
        ret="<table class=\"\">"
        delays=ScheduleDelay.objects.filter(schedule__id=self.schedule.id).order_by('delay')

        for d in delays:
            hori=horizon(self.date,d.delay)
            if hori<=datetime.now().date():
                ret=ret+"<tr class=\"\"><td><b>"
                l=d.attributes.values_list("value")
                ret=ret+"<b>"+hori.strftime("%a-%b-%d")+"</b></td><td><b>"
                for e in l: 
                    ret=ret+e[0]+" "
                ret=ret+"</b></td></tr>"
            else:
                ret=ret+"<tr class=\"\"><td>"
                l=d.attributes.values_list("value")
                ret=ret+hori.strftime("%a-%b-%d")+"</td><td>"
                for e in l: 
                    ret=ret+e[0]+" " 
                ret=ret+"</td></tr>"           
        return ret+"</table>"
    timeline.allow_tags=True
    timeline.short_description = _('timeline')

    class Meta:
        verbose_name = _("Repository")
        verbose_name_plural = _("Repositories")
        unique_together=(("name","version"),)
        permissions = (("can_save_repository", "Can save Repository"),)


class UserProfile(UserSystem):
    info="For designate the password use <a href=\"/migasfree/auth/password/\">change password form</a>."
    version= models.ForeignKey(Version,verbose_name=_("version"))

    # Use UserManager to get the create_user method, etc.
    objects = UserManager()


    def save(self):
        if not self.password.startswith("sha1$"):
            super(UserProfile, self).set_password(self.password)
        super(UserProfile, self).save() # Call the "real" save() method



    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("Users Profile")
        permissions = (("can_save_userprofile", "Can save User Profile"),)



class Login(models.Model):
    date= models.DateTimeField(_("date"),default=0)
    computer = models.ForeignKey(Computer,verbose_name=_("computer"))
    user= models.ForeignKey(User,verbose_name=_("user"))
    attributes = models.ManyToManyField(Attribute,null=True, blank=True,verbose_name=_("attributes"))

    def linkComputer(self):
        return '<a href="%s">%s</a>' % ( "../Computer/"+str(self.computer.id), self.computer.name )
    linkComputer.allow_tags=True

    def linkUser(self):
        return '<a href="%s">%s</a>' % ( "../User/"+str(self.user.id), self.user.name )
    linkUser.allow_tags=True

    def __unicode__(self):
        return str(self.id)+" - "+self.user.name+" - "+self.computer.name 

    class Meta:
        verbose_name = _("Login")
        verbose_name_plural = _("Logins")
        unique_together=(("computer","user"),)
        permissions = (("can_save_login", "Can save Login"),)


class Query(models.Model):
    name = models.CharField(_("name"),max_length=50,null=True, blank=True,unique=True)
    description = models.TextField(_("description"),null=True, blank=True)
    code = models.TextField(_("code"),null=True, blank=True,help_text="Code Django: VERSION=user.version, query=QuerySet, fields=list of QuerySet fields names to show, titles=list of QuerySet fields titles",default="query=Package.objects.filter(version=VERSION).filter(Q(repository__id__exact=None))\nfields=('id','name','store__name')\ntitles=('id','name','store')")
    parameters =models.TextField(_("parameters"),null=True, blank=True,help_text="Code Django: ")

    def __unicode__(self):
        return self.name 

    class Meta:
        verbose_name = _("Query")
        verbose_name_plural = _("Queries")
        permissions = (("can_save_query", "Can save Query"),)


class DeviceType(models.Model):
    name = models.CharField(_("name"),max_length=50,null=True, blank=True,unique=True)
    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = _("Device (Type)")
        verbose_name_plural = _("Device (Types)")
        permissions = (("can_save_devicetype", "Can save Device Type"),)

class DeviceManufacturer(models.Model):
    name = models.CharField(_("name"),max_length=50,null=True, blank=True,unique=True)
    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = _("Device (Manufacturer)")
        verbose_name_plural = _("Device (Manufacturers)")
        permissions = (("can_save_devicemanufacturer", "Can save Device Manufacturer"),)

class DeviceConnection(models.Model):
    name = models.CharField(_("name"),max_length=50,null=True, blank=True)
    fields = models.CharField(_("fields"),max_length=50,null=True, blank=True)
    code = models.TextField(_("code"),null=True, blank=True,help_text="code")
    devicetype = models.ForeignKey(DeviceType,verbose_name=_("device type"))

    def __unicode__(self):
        return u'(%s) %s' % (self.devicetype.name,self.name)

    def save(self):
        self.code=self.code.replace("\r\n","\n")
        super(DeviceConnection, self).save() # Call the "real" save() method

    class Meta:
        verbose_name = _("Device (Connection)")
        verbose_name_plural = _("Device (Connections)")
        unique_together=(("devicetype","name"),)
        permissions = (("can_save_deviceconnection", "Can save Device Connection"),)

class DeviceModel(models.Model):
    name = models.CharField(_("name"),max_length=50,null=True, blank=True)
    manufacturer = models.ForeignKey(DeviceManufacturer,verbose_name=_("manufacturer"))
    devicetype = models.ForeignKey(DeviceType,verbose_name=_("type"))
    filename = models.CharField(_("file name"),max_length=100,null=True, blank=True)
    connections = models.ManyToManyField(DeviceConnection,null=True, blank=True,verbose_name=_("connections"))
    precode = models.TextField(_("precode"),null=True, blank=True,help_text="precode")
    postcode = models.TextField(_("postcode"),null=True, blank=True,help_text="postcode")
    def __unicode__(self):
        return u'%s' % (self.name)
    def save(self):
        self.name=self.name.replace(" ","_")
        self.precode=self.precode.replace("\r\n","\n")
        self.postcode=self.postcode.replace("\r\n","\n")
        super(DeviceModel, self).save() # Call the "real" save() method
    class Meta:
        verbose_name = _("Device (Model)")
        verbose_name_plural = _("Device (Models)")
        unique_together=(("devicetype","manufacturer","name"),)
        permissions = (("can_save_devicemodel", "Can save Device Model"),)

class Device(models.Model):

    def device_connection_name(self):
        return ("%s" % (self.connection.name))
    device_connection_name.short_description = _('Port')
    def device_connection_type(self):
        return ("%s" % (self.connection.devicetype.name))
    device_connection_type.short_description = _('Type')
    def device_manufacturer_name(self):
        return ("%s" % (self.model.manufacturer.name))
    device_manufacturer_name.short_description = _('Manufacturer')


    name = models.CharField(_("name"),max_length=50,null=True, blank=True)
    model = models.ForeignKey(DeviceModel,verbose_name=_("model"))
    connection = models.ForeignKey(DeviceConnection,verbose_name=_("connection"))
    values=models.TextField(_("code"),null=True, blank=True,help_text=_("code"))
    def __unicode__(self):
        return u'%s' % (self.name)
    class Meta:
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        unique_together=(("connection","name"),)
        permissions = (("can_save_device", "Can save Device"),)


class Checking(models.Model):
    """
    For each register of this model, migasfree will show in the section Status of main menu the result of this 'checking'.
    The system only will show the checking if 'result' <> 0
    """
    name=models.CharField(_("name"),max_length=50,null=True, blank=True,help_text=_("name"),unique=True)
    description=models.TextField(_("description"),null=True, blank=True,help_text=_("description"))
    code=models.TextField(_("code"),null=True, blank=True,help_text="Code django. <br><b>VARIABLES TO SETTINGS:</b><br><b>result</b>: a number. If result<>0 the checking is show in the section Status. Default is 0<br><b>icon</b>: name of icon to show localizate in '/repo/icons'. Default is 'information.png'<br><b>url</b>: link. Default is '/migasfree/main'<br><b>message</b>: The text to show. Default is the field name.")
    active = models.BooleanField(_("active"),default=True,help_text="")


    def save(self):
        self.code=self.code.replace("\r\n","\n")
        super(Checking, self).save() # Call the "real" save() method
    def __unicode__(self):
        return u'%s' % (self.name)
    class Meta:
        verbose_name = _("Checking")
        verbose_name_plural = _("Checkings")
        permissions = (("can_save_checking", "Can save Checking"),)


class AutoCheckError(models.Model):
    """
    This model is used to autocheck the errors and marked as 'check' when they are introducing in the system (Sometimes the Package Management System, in the clients, return a string error when in reliaty it is only a warning)
    The origen of this problem is that the package is bad packed.
    """
    message=models.TextField(_("message"),null=True, blank=True,help_text=_("Text of error that is only a warning. You can copy/paste from the field 'error' of a Error."))

    def save(self):
        self.message=self.message.replace("\r\n","\n")
        super(AutoCheckError, self).save()

    def __unicode__(self):
        return u'%s' % (self.message)
    class Meta:
        verbose_name = _("Auto Check Error")
        verbose_name_plural = _("Auto Check Errors")
        permissions = (("can_save_autocheckerror", "Can save Auto Check Error"),)








