# -*- coding: utf-8 -*-

from import_export import resources

from .models import Computer


class ComputerResource(resources.ModelResource):
    class Meta:
        model = Computer
        exclude = ('history_sw', 'software')
