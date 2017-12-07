# -*- coding: utf-8 -*-

from import_export import resources

from .models import Computer


class ComputerResource(resources.ModelResource):
    class Meta:
        model = Computer
        exclude = (
            'software_history', 'software_inventory',
            'sync_attributes', 'sync_user',
        )
