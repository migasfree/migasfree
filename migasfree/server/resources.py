# -*- coding: utf-8 -*-

from import_export import resources
from import_export.fields import Field

from .models import Computer
from .models import Attribute


class ComputerResource(resources.ModelResource):
    def dehydrate_project(self, computer):
        return computer.project.name

    def dehydrate_sync_user(self, computer):
        return u'{} ({})'.format(computer.sync_user.name, computer.sync_user.fullname)

    class Meta:
        model = Computer
        exclude = (
            'software_history',
            'software_inventory',
            'sync_attributes',
            'default_logical_device',
        )


class AttributeResource(resources.ModelResource):
    computers = Field()
    prefix = Field()

    def dehydrate_computers(self, attribute):
        return attribute.total_computers

    def dehydrate_prefix(self, attribute):
        return attribute.property_att.prefix

    class Meta:
        model = Attribute
        export_order = ('id', 'property_att', 'prefix', 'value', 'description', 'computers')
