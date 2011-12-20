from django.db.models import Q
from django.utils.html import escape
from migasfree.server.models import *
from ajax_select import LookupChannel



class AttributeLookup(LookupChannel):

    model = Attribute

    def get_query(self,q,request):
        return Attribute.objects.filter( Q(value__icontains=q) | Q(description__icontains=q) | Q(property_att__prefix__icontains=q)).order_by('value')


    def get_result(self,obj):
        return unicode(obj)
        
    def format_match(self,obj):
        return self.format_item_display(obj)

    def format_item_display(self,obj):
#        return u"%s<div><i>%s</i></div>" % (escape(obj.__unicode__),escape(obj.description))
	return u"%s-%s %s" % (escape(obj.property_att.prefix),escape(obj.value),escape(obj.description))

    def can_add(self,user,model):
        return False


class PackageLookup(LookupChannel):
    model = Package

    def get_query(self,q,request):
#        return Attribute.objects.filter(value__icontains=q or description__icontains=q).order_by('value')
        return Package.objects.filter(Q(name__icontains=q)).order_by('name')

    def get_result(self,obj):
        return unicode(obj)
        
    def format_match(self,obj):
        return self.format_item_display(obj)

    def format_item_display(self,obj):
#        return u"%s<div><i>%s</i></div>" % (escape(obj.__unicode__),escape(obj.description))
	return u"%s" % escape(obj.name)

    def can_add(self,user,model):
        return False

