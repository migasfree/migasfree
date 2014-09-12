# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.html import format_html

from migasfree.server.functions import trans

# Programming Languages for Properties and FaultDefs
LANGUAGES_CHOICES = (
    (0, 'bash'),
    (1, 'python'),
    (2, 'perl'),
    (3, 'php'),
    (4, 'ruby'),
    (5, 'cmd'),
)


class MigasLink(object):
    _actions = None
    _exclude_links = []
    _include_links = []

    def link(self, default=False):
        related_objects = self._meta.get_all_related_objects_with_model() \
            + self._meta.get_all_related_m2m_objects_with_model()
        if (len(related_objects) == 0 and self._actions is None) or default:
            return '<a href="%s">%s</a>' % (
                reverse(
                    'admin:server_%s_change' % self._meta.model_name,
                    args=(self.id, )
                ),
                self.__unicode__()
            )

        _link = '<span class="sr-only">%s</span><a href="%s" class="btn btn-xs">%s</a>' % (
            self.__unicode__(),
            reverse(
                'admin:server_%s_change' % self._meta.model_name,
                args=(self.id, )
            ),
            self.__unicode__()
        )

        _link += '<button type="button" ' + \
            'class="btn btn-default dropdown-toggle" data-toggle="dropdown">' + \
            '<span class="caret"></span>' + \
            '<span class="sr-only">' + trans("Toggle Dropdown") + \
            '</span></button>'

        related_data = ''
        if self._actions is not None:
            related_data += '<li role="presentation" class="dropdown-header">%s</li>' % trans("Actions")
            for item in self._actions:
                related_data += '<li><a href="%(href)s">%(protocol)s</a></li>' % {
                    'href': item[1],
                    'protocol': item[0]
                }

            related_data += '<li role="presentation" class="divider"></li>'

        related_data += '<li role="presentation" class="dropdown-header">%s</li>' % trans("Related data")
        for related_object, _ in related_objects:
            if not "%s - %s" % (related_object.model._meta.model_name,related_object.field.name) in self._exclude_links:
                try:
                    related_link = reverse(
                        'admin:server_%s_changelist'
                        % related_object.model._meta.model_name
                    )
                    related_data += '<li><a href="%s?%s__exact=%d">%s [%s]</a></li>' % (
                        related_link,
                        related_object.field.name,
                        self.id,
                        trans(related_object.model._meta.verbose_name_plural),
                        trans(related_object.field.name)
                    )
                except:
                    pass

        for _include in self._include_links:
            try:
                (_modelname, _fieldname) = _include.split(" - ")
                related_link = reverse(
                    'admin:server_%s_changelist'
                    % _modelname
                )
                related_data += '<li><a href="%s?%s__exact=%d">%s [%s]</a></li>' % (
                    related_link,
                    _fieldname,
                    self.id,
                    trans(_modelname),
                    trans(_fieldname)
                )
            except:
                pass

        return format_html(
            '<div class="btn-group btn-group-xs">' +
            _link.replace('{', '{{').replace('}', '}}') +
            '<ul class="dropdown-menu" role="menu">' +
            related_data.replace('{', '{{').replace('}', '}}') +
            '</ul></div>'
        )

    link.allow_tags = True
    link.short_description = ''
