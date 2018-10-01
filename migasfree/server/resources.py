# -*- coding: utf-8 -*-

from import_export import resources
from import_export.fields import Field

from .models import Computer
from .models import Attribute


class ComputerResource(resources.ModelResource):
    class Meta:
        model = Computer
        exclude = (
            'software_history', 'software_inventory',
            'sync_attributes', 'sync_user',
        )


class AttributeResource(resources.ModelResource):
    computers = Field()
    prefix = Field()

    class Meta:
        model = Attribute
        export_order = ('id', 'property_att', 'prefix', 'value', 'description', 'computers')

    def dehydrate_computers(self, attribute):
        return attribute.total_computers

    def dehydrate_prefix(self, attribute):
        return attribute.property_att.prefix
