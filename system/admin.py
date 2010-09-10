# -*- encoding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from migasfree.system.models import Package
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.shortcuts import redirect

from migasfree.system.models import Property
from migasfree.system.models import Attribute
from migasfree.system.models import User
from migasfree.system.models import Store
from migasfree.system.models import Repository
from migasfree.system.models import Pms
from migasfree.system.models import Version
from migasfree.system.models import Computer
from migasfree.system.models import Variable
from migasfree.system.models import UserProfile
from migasfree.system.models import Error
from migasfree.system.models import Login
from migasfree.system.models import Fault
from migasfree.system.models import FaultDef
from migasfree.system.models import Query
from migasfree.system.models import Schedule
from migasfree.system.models import ScheduleDelay
from migasfree.system.models import DeviceManufacturer
from migasfree.system.models import DeviceType
from migasfree.system.models import DeviceModel
from migasfree.system.models import DeviceConnection
from migasfree.system.models import Device
from migasfree.system.models import Checking
from migasfree.system.models import AutoCheckError

admin.site.register(DeviceType)
admin.site.register(DeviceManufacturer)
admin.site.register(DeviceConnection)
admin.site.register(UserProfile)
admin.site.register(AutoCheckError)



def user_version(user):
    user_id=user.id
    try:
        version=UserProfile.objects.get(id=user_id).version.id
    except:
        version=None
    return version



class VersionAdmin(admin.ModelAdmin):
    list_display = ('name','pms','computerbase')
    actions=None
admin.site.register(Version,VersionAdmin)


class CheckingAdmin(admin.ModelAdmin):
    list_display = ('name','active')
    list_filter = ('active',)
admin.site.register(Checking,CheckingAdmin)

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name','device_connection_type','device_manufacturer_name','model','device_connection_name','values',)
    list_filter = ('model',)
    search_fields = ('connection__devicetype__name','manufacturer__name')
admin.site.register(Device, DeviceAdmin)

class DeviceModelAdmin(admin.ModelAdmin):
    list_display = ('name','manufacturer','devicetype',)
    list_filter = ('devicetype','manufacturer',)
    search_fields = ('connection__devicetype__name',)
admin.site.register(DeviceModel, DeviceModelAdmin)


class PmsAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Pms, PmsAdmin)

class StoreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    actions = ['information','download']

    def download(self,request,queryset):
        return redirect("/repo/"+queryset[0].version.name+"/STORES/"+queryset[0].name+"/")
    download.short_description = _("Download")

    def information(self,request,queryset):
        return redirect("/migasfree/info/STORES/"+queryset[0].name+"/")
    information.short_description = _("Information of Package")

admin.site.register(Store, StoreAdmin)


class PropertyAdmin(admin.ModelAdmin):
    list_display = ('prefix','name','active','kind','auto',)
    list_filter = ('active',)
    ordering = ('name',)
    search_fields = ('user__name','user__fullname','computer__name')
admin.site.register(Property, PropertyAdmin)


class AttributeAdmin(admin.ModelAdmin):
    list_display = ('value','description','linkProperty')
    list_filter = ('property_att',)
    ordering = ('property_att','value',)
    search_fields = ('value','description')
admin.site.register(Attribute,AttributeAdmin)


class LoginAdmin(admin.ModelAdmin):
    list_display = ('id','linkUser','linkComputer','date')
    list_filter = ('date',)
    ordering = ('user','computer')
    search_fields = ('user__name','user__fullname','computer__name')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "attributes":
            kwargs["queryset"] = Attribute.objects.filter(property_att__active=True)
            kwargs['widget'] = FilteredSelectMultiple(db_field.verbose_name, (db_field.name in self.filter_vertical))
            return db_field.formfield(**kwargs)
        return super(LoginAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(Login, LoginAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = ('name','fullname')
    ordering = ('name',)
    search_fields = ('name','fullname')
admin.site.register(User, UserAdmin)


class ErrorAdmin(admin.ModelAdmin):
    list_display = ('id','linkComputer','checked','date','error')
    list_filter = ('checked','date',)
    ordering = ('date','computer')
    search_fields = ('date','computer__name','error')

    actions = ['checked_OK']

    def checked_OK(self,request,queryset):
        for error in queryset:
            error.checked=True
            error.save()
        return redirect("/migasfree/admin/system/error/?checked__exact=0")
    checked_OK.short_description = _("Checking is O.K.")


admin.site.register(Error, ErrorAdmin)


class FaultAdmin(admin.ModelAdmin):
    list_display = ('id','linkComputer','checked','date','text','faultdef',)
    list_filter = ('checked','date','faultdef',)
    ordering = ('date','computer',)
    search_fields = ('date','computer__name','fault',)

    actions = ['checked_OK']

    def checked_OK(self,request,queryset):
        for fault in queryset:
            fault.checked=True
            fault.save()
        return redirect("/migasfree/admin/system/fault/?checked__exact=0")
    checked_OK.short_description = _("Checking is O.K.")
admin.site.register(Fault, FaultAdmin)

class FaultDefAdmin(admin.ModelAdmin): 
    list_display = ('name','active',)
    list_filter = ('active',)
    ordering = ('name',)
    search_fields = ('name','function',)
admin.site.register(FaultDef, FaultDefAdmin)


class ComputerAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip','version',)
    ordering = ('name',)
    list_filter = ('version',)
    search_fields = ('name','ip','mac')
admin.site.register(Computer, ComputerAdmin)


class VariableAdmin(admin.ModelAdmin):
    list_display = ('name','value')
    ordering = ('name',)
    search_fields = ('name',)
admin.site.register(Variable, VariableAdmin)


class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'date', 'schedule','timeline', )
    list_filter = ('active',)
    ordering = ('name','packages__name')
    search_fields = ('name','packages__name')
    filter_horizontal = ('attributes','packages')
    actions = None

    # QuerySet filter by user version.
    def queryset(self, request):
        if request.user.is_superuser:
            qs= self.model._default_manager.get_query_set()
        else:
            qs = self.model._default_manager.get_query_set().filter(version=user_version(request.user))
        return qs

    # Packages filter by user version
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "packages":
            kwargs["queryset"] = Package.objects.filter(version=user_version(request.user))
            kwargs['widget'] = FilteredSelectMultiple(db_field.verbose_name, (db_field.name in self.filter_vertical))
            return db_field.formfield(**kwargs)

        if db_field.name == "attributes":
            kwargs["queryset"] = Attribute.objects.filter(property_att__active=True)
            kwargs['widget'] = FilteredSelectMultiple(db_field.verbose_name, (db_field.name in self.filter_vertical))
            return db_field.formfield(**kwargs)
        return super(RepositoryAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(Repository, RepositoryAdmin)



class ScheduleDelayAdmin(admin.ModelAdmin):
    list_display = ('delay','schedule','list_attributes',)
    list_filter = ('schedule',)
    ordering = ('schedule','delay',)
    search_fields = ('schedule','attributes_value',)
    # Packages filter by identyties active
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "attributes":
            kwargs["queryset"] = Attribute.objects.filter(property_att__active=True)
            kwargs['widget'] = FilteredSelectMultiple(db_field.verbose_name, (db_field.name in self.filter_vertical))
            return db_field.formfield(**kwargs)
        return super(ScheduleDelayAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
admin.site.register(ScheduleDelay, ScheduleDelayAdmin)


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('name','description')
admin.site.register(Schedule, ScheduleAdmin)


class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'store')
    list_filter = ('store',)
    search_fields = ('name','store__name')
    ordering = ('name',)


    actions = ['information','download']

    def information(self,request,queryset):
        return redirect("/migasfree/info/STORES/"+queryset[0].store.name+"/"+queryset[0].name+"/")
    information.short_description = _("Information of Package")

    def download(self,request,queryset):
        return redirect("/repo/"+queryset[0].version.name+"/STORES/"+queryset[0].store.name+"/"+queryset[0].name)
    download.short_description = _("Download")

admin.site.register(Package, PackageAdmin)


class QueryAdmin(admin.ModelAdmin):
    list_display = ('name','description',)
    actions = ['runQuery']

    def runQuery(self,request,queryset):
        for query in queryset:
            return redirect("/migasfree/query/?id="+str(query.id))
    runQuery.short_description = _("Run Query")

admin.site.register(Query, QueryAdmin)



