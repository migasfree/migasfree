# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils.html import escape
from django.conf import settings

from ajax_select import register, LookupChannel

from .models import (
    Attribute,
    Tag,
    Package,
    Property,
    DeviceLogical,
    UserProfile,
    Computer
)


@register('attribute')
class AttributeLookup(LookupChannel):
    model = Attribute

    def get_query(self, q, request):
        prps = Property.objects.all().values_list('prefix', flat=True)
        if q[0:Property.PREFIX_LEN].upper() in (prop.upper() for prop in prps) \
                and len(q) > (Property.PREFIX_LEN + 1):
            return self.model.objects.filter(
                property_att__prefix__icontains=q[0:Property.PREFIX_LEN]
            ).filter(
                value__icontains=q[Property.PREFIX_LEN + 1:]
            ).filter(
                property_att__active=True
            ).order_by('value')
        else:
            return self.model.objects.filter(
                Q(value__icontains=q) |
                Q(description__icontains=q) |
                Q(property_att__prefix__icontains=q)
            ).filter(property_att__active=True).order_by('value')

    def format_match(self, obj):
        return escape(obj.__str__())

    def format_item_display(self, obj):
        return obj.link()

    def can_add(self, user, model):
        return False

    def get_objects(self, ids):
        if settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0] != "id":
            return self.model.objects.filter(
                pk__in=ids).filter(
                    ~Q(property_att__prefix='CID')).order_by(
                        'property_att',
                        'value'
            ) | self.model.objects.filter(
                pk__in=ids).filter(
                    property_att__prefix='CID'
                ).order_by(
                    'description'
            )
        else:
            return self.model.objects.filter(pk__in=ids).order_by(
                'property_att',
                'value'
            )


@register('attribute_computers')
class AttributeComputersLookup(LookupChannel):
    model = Attribute

    def get_query(self, q, request):
        prps = Property.objects.all().values_list('prefix', flat=True)
        if q[0:Property.PREFIX_LEN].upper() in (prop.upper() for prop in prps) \
                and len(q) > (Property.PREFIX_LEN + 1):
            return self.model.objects.filter(
                property_att__prefix__icontains=q[0:Property.PREFIX_LEN]
            ).filter(
                value__icontains=q[Property.PREFIX_LEN + 1:]
            ).filter(
                property_att__active=True
            ).order_by('value')
        else:
            return self.model.objects.filter(
                Q(value__icontains=q) |
                Q(description__icontains=q) |
                Q(property_att__prefix__icontains=q)
            ).filter(
                property_att__active=True
            ).order_by('value')

    def format_match(self, obj):
        return "%s (total %s)" % (
            escape(obj.__str__()),
            escape(obj.total_computers(UserProfile.get_logged_version()))
        )

    def format_item_display(self, obj):
        return "%s (total %s)" % (
            obj.link(),
            escape(obj.total_computers(UserProfile.get_logged_version()))
        )

    def can_add(self, user, model):
        return False

    def get_objects(self, ids):
        if settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0] != "id":
            return self.model.objects.filter(
                pk__in=ids).filter(
                    ~Q(property_att__prefix='CID')).order_by(
                        'property_att',
                        'value'
            ) | self.model.objects.filter(
                pk__in=ids).filter(
                    property_att__prefix='CID'
                ).order_by(
                    'description'
            )
        else:
            return self.model.objects.filter(pk__in=ids).order_by(
                'property_att',
                'value'
            )


@register('package')
class PackageLookup(LookupChannel):
    model = Package

    def get_query(self, q, request):
        version_id = request.GET.get('version_id', None)
        queryset = self.model.objects.filter(name__icontains=q).order_by('name')
        if version_id:
            queryset = queryset.filter(version__id=version_id)

        return queryset

    def format_match(self, obj):
        return escape(obj.name)

    def format_item_display(self, obj):
        return obj.link()

    def can_add(self, user, model):
        return False

    def get_objects(self, ids):
        return self.model.objects.filter(pk__in=ids).order_by('name')


@register('tag')
class TagLookup(LookupChannel):
    model = Tag

    def get_query(self, q, request):
        return self.model.objects.filter(
            property_att__active=True,
            property_att__tag=True
        ).filter(
            Q(value__icontains=q) |
            Q(description__icontains=q) |
            Q(property_att__prefix__icontains=q)
        ).order_by('value')

    def format_match(self, obj):
        return "%s-%s %s" % (
            escape(obj.property_att.prefix),
            escape(obj.value),
            escape(obj.description)
        )

    def format_item_display(self, obj):
        return obj.link()

    def can_add(self, user, model):
        return False

    def get_objects(self, ids):
        return self.model.objects.filter(pk__in=ids).order_by(
            'property_att',
            'value'
        )


@register('devicelogical')
class DeviceLogicalLookup(LookupChannel):
    model = DeviceLogical

    def get_query(self, q, request):
        return self.model.objects.filter(device__name__icontains=q)

    def format_match(self, obj):
        return escape(obj.__str__())

    def format_item_display(self, obj):
        return obj.link()

    def can_add(self, user, model):
        return False


@register('computer')
class ComputerLookup(LookupChannel):
    model = Computer

    def get_query(self, q, request):
        if settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0] == "id":
            return self.model.objects.filter(id__exact=q)
        else:
            return self.model.objects.filter(
                Q(id__exact=q) |
                Q(**{
                    '%s__icontains' %
                    settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0]: q
                })
            )

    def format_match(self, obj):
        return obj.__str__()

    def format_item_display(self, obj):
        return obj.link()

    def can_add(self, user, model):
        return False

    def reorder(self, mylist):
        return [row.id for row in Computer.objects.filter(
            pk__in=mylist
        ).order_by(settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0])]

    def get_objects(self, ids):
        """
        Get the currently selected objects when editing an existing model
        """
        # return in the same order as passed in here
        # this will be however the related objects Manager returns them
        # which is not guaranteed to be the same order
        # they were in when you last edited
        # see OrderedManyToMany.md
        lst = []
        for item in ids:
            if item.__class__.__name__ == "Computer":
                lst.append(int(item.pk))
            else:
                lst.append(int(item))

        things = self.model.objects.in_bulk(lst)
        if settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0] == "id":
            return [things[aid] for aid in lst if aid in things]
        else:
            return [things[aid] for aid in self.reorder(lst) if aid in things]
