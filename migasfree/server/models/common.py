# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext
from django.template.loader import render_to_string

from ..functions import vl2s

# Programming Languages for Properties and Fault Definitions
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
        related_objects = [
            (f, f.model if f.model != self else None)
            for f in self._meta.get_fields()
            if (f.one_to_many or f.one_to_one)
            and f.auto_created and not f.concrete
        ] + [
            (f, f.model if f.model != self else None)
            for f in self._meta.get_fields(include_hidden=True)
            if f.many_to_many and f.auto_created
        ]

        objs = [
            (f, f.model if f.model != self else None)
            for f in self._meta.get_fields()
            if f.many_to_many and not f.auto_created
        ]

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
                    related_data.append({
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
                _modelname, _fieldname = _include.split(" - ")
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

        if self._meta.model_name == 'computer':
            related_data.append({
                'url': reverse('computer_events', args=(self.id,)),
                'text': '%s [%s]' % (
                    ugettext('Events'),
                    ugettext(self._meta.model_name)
                )
            })

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
