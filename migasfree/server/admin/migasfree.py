# -*- coding: utf-8 -*-

from django.utils.translation import ugettext

from import_export.admin import ExportActionModelAdmin


class MigasAdmin(ExportActionModelAdmin):
    list_display_links = None

    @staticmethod
    def boolean_field(field):
        style = 'fa-check boolean-yes'
        text = ugettext('Yes')
        if not field:
            style = 'fa-times boolean-no'
            text = ugettext('No')

        return '<span class="fa %s"><span class="sr-only">%s</span></span>' % (
            style, text
        )
