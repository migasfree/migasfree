# -*- coding: utf-8 -*-

from django.utils.translation import ugettext

from import_export.admin import ExportActionModelAdmin


class MigasAdmin(ExportActionModelAdmin):
    list_display_links = None

    def boolean_field(self, field):
        if field:
            ret = '<span class="fa fa-check boolean-yes">' \
                + '<span class="sr-only">%s</span></span>' % ugettext('Yes')
        else:
            ret = '<span class="fa fa-times boolean-no">' \
                + '<span class="sr-only">%s</span></span>' % ugettext('No')

        return ret
