# -*- coding: utf-8 -*-

from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import Permission, Group
from django.utils.html import escape

from ajax_select import register, LookupChannel

from .models import (
    Attribute,
    ServerAttribute,
    Package,
    Property,
    DeviceLogical,
    Computer,
    UserProfile,
)


@register('user_profile')
class UserProfileLookup(LookupChannel):
    model = UserProfile

    def can_add(self, user, model):
        return False

    def get_query(self, q, request):
        return self.model.objects.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        ).order_by('username')

    def format_item_display(self, obj):
        if obj.first_name or obj.last_name:
            return u'{} ({})'.format(
                obj.link(),
                u' '.join(filter(None, [obj.first_name, obj.last_name]))
            )

        return obj.link()

    def format_match(self, obj):
        return escape("%s (%s)" % (obj.__str__(), u' '.join(filter(None, [obj.first_name, obj.last_name]))))


@register('domain_admin')
class DomainAdminLookup(UserProfileLookup):
    def get_query(self, q, request):
        domain_admin = Group.objects.get(name="Domain Admin")
        return self.model.objects.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q),
            groups__in=[domain_admin]
        ).order_by('username')


@register('permission')
class PermissionLookup(LookupChannel):
    model = Permission

    def get_query(self, q, request):
        return self.model.objects.filter(
            Q(name__icontains=q) | Q(codename__icontains=q)
        ).order_by('name')

    def format_match(self, obj):
        return escape(obj.__str__())

    def format_item_display(self, obj):
        return obj.__str__()

    def get_objects(self, ids):
        return self.model.objects.filter(pk__in=ids).order_by('name')


@register('attribute')
class AttributeLookup(LookupChannel):
    model = Attribute

    def get_query(self, q, request):
        properties = Property.objects.values_list('prefix', flat=True)
        if q[0:Property.PREFIX_LEN].upper() \
                in (item.upper() for item in properties) \
                and len(q) > (Property.PREFIX_LEN + 1):
            queryset = self.model.objects.scope(request.user.userprofile).filter(
                property_att__prefix__icontains=q[0:Property.PREFIX_LEN],
                value__icontains=q[Property.PREFIX_LEN + 1:],
                property_att__enabled=True
            )
        else:
            queryset = self.model.objects.scope(request.user.userprofile).filter(
                Q(value__icontains=q) |
                Q(description__icontains=q) |
                Q(property_att__prefix__icontains=q)
            ).filter(property_att__enabled=True)

        # exclude available and unsubscribed computers (inactive)
        inactive_computers = [
            str(x) for x in Computer.inactive.values_list('id', flat=True)
        ]
        queryset = queryset.exclude(
            property_att__prefix='CID',
            value__in=inactive_computers
        ).order_by('value')

        return queryset

    def format_match(self, obj):
        return escape(obj.__str__())

    def format_item_display(self, obj):
        return obj.link()

    def can_add(self, user, model):
        return False

    def get_objects(self, objects):
        ids = [obj.pk for obj in objects]
        if settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0] != "id":
            return self.model.objects.filter(
                pk__in=ids
            ).filter(
                ~Q(property_att__prefix='CID')
            ).order_by(
                'property_att',
                'value'
            ) | self.model.objects.filter(
                pk__in=ids,
                property_att__prefix='CID'
            ).order_by(
                'description'
            )
        else:
            return self.model.objects.filter(
                pk__in=ids
            ).order_by(
                'property_att',
                'value'
            )


@register('package')
class PackageLookup(LookupChannel):
    model = Package

    def get_query(self, q, request):
        project_id = request.GET.get('project_id', None)
        queryset = self.model.objects.scope(request.user.userprofile).filter(name__icontains=q).order_by('name')
        if project_id:
            queryset = queryset.filter(project__id=project_id)

        return queryset

    def format_match(self, obj):
        return escape(obj.name)

    def format_item_display(self, obj):
        return obj.link()

    def can_add(self, user, model):
        return False

    def get_objects(self, objects):
        ids = [obj.pk for obj in objects]
        return self.model.objects.filter(pk__in=ids).order_by('name')


@register('tag')
class TagLookup(LookupChannel):
    model = ServerAttribute

    def get_query(self, q, request):
        return self.model.objects.scope(request.user.userprofile).filter(
            property_att__enabled=True,
            property_att__sort='server'
        ).filter(
            Q(value__icontains=q) |
            Q(description__icontains=q) |
            Q(property_att__prefix__icontains=q)
        ).order_by('value')

    def format_match(self, obj):
        return u'{}-{} {}'.format(
            escape(obj.property_att.prefix),
            escape(obj.value),
            escape(obj.description)
        )

    def format_item_display(self, obj):
        return obj.link()

    def can_add(self, user, model):
        return False

    def get_objects(self, objects):
        ids = [obj.pk for obj in objects]
        return self.model.objects.filter(
            pk__in=ids
        ).order_by(
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
            return self.model.objects.scope(request.user.userprofile).filter(id__exact=q)
        else:
            return self.model.objects.scope(request.user.userprofile).filter(
                Q(id__exact=q) |
                Q(**{
                    '{}__icontains'.format(
                        settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0]
                    ): q
                })
            ).filter(
                ~Q(status__in=['available', 'unsubscribed'])
            )

    def format_match(self, obj):
        return obj.__str__()

    def format_item_display(self, obj):
        return obj.link()

    def can_add(self, user, model):
        return False

    def reorder(self, ids):
        return [row.id for row in Computer.objects.filter(
            pk__in=ids
        ).order_by(settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0])]

    def get_objects(self, objects):
        ids = [obj.pk for obj in objects]

        lst = []
        for item in ids:
            if item.__class__.__name__ == "Computer":
                lst.append(int(item.pk))
            else:
                lst.append(int(item))

        things = self.model.objects.in_bulk(lst)
        if settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0] == "id":
            return [things[aid] for aid in lst if aid in things]

        return [things[aid] for aid in self.reorder(lst) if aid in things]
