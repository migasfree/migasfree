# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext
from django.template.loader import render_to_string

from ..functions import vl2s

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

    def link(self):
        related_objects = self._meta.get_all_related_objects_with_model() \
            + self._meta.get_all_related_m2m_objects_with_model()

        objs = self._meta.get_m2m_with_model()

        action_data = []
        if self._actions is not None and any(self._actions):
            for item in self._actions:
                action_data.append({'url': item[1], 'text': item[0]})

        related_data = []
        for obj, _ in objs:
            try:
                _name = obj.related.field.related.parent_model.__name__.lower()
                if _name == "attribute":
                    _name = "att"

                related_link = reverse(
                    'admin:%s_%s_changelist' % (
                        obj.related.model._meta.app_label,
                        _name)
                    )
                values = vl2s(
                    self.__getattribute__(obj.related.field.name)
                ).replace("[", "").replace("]", "")
                if values:
                    realted_data.append({
                        'url': '%s?id__in=%s' % (related_link, values),
                        'text': ugettext(obj.related.field.name)
                    })
            except:
                pass

        for related_object, _ in related_objects:
            if not "%s - %s" % (
                related_object.related_model._meta.model_name,
                related_object.field.name
            ) in self._exclude_links:
                try:
                    related_link = reverse(
                        'admin:server_%s_changelist'
                        % related_object.related_model._meta.model_name
                    )
                    related_data.append({
                        'url': '%s?%s__exact=%d' % (
                            related_link,
                            related_object.field.name,
                            self.id
                        ),
                        'text': '%s [%s]' % (
                            ugettext(
                                related_object.related_model._meta.verbose_name_plural
                            ),
                            ugettext(related_object.field.name)
                        )
                    })
                except:
                    pass

        for _include in self._include_links:
            try:
                (_modelname, _fieldname) = _include.split(" - ")
                related_link = reverse(
                    'admin:server_%s_changelist'
                    % _modelname
                )
                related_data.append({
                    'url': '%s?%s__exact=%d' % (
                        related_link,
                        _fieldname,
                        self.id
                    ),
                    'text': '%s [%s]' % (
                        ugettext(_modelname),
                        ugettext(_fieldname)
                    )
                })
            except:
                pass

        return render_to_string(
            'includes/migas_link.html',
            {
                'lnk': {
                    'url': reverse(
                        'admin:server_%s_change' % self._meta.model_name,
                        args=(self.id,)
                    ),
                    'text': self.__str__(),
                    'actions': action_data,
                    'related': related_data
                }
            }
        )

    link.allow_tags = True
    link.short_description = ''
