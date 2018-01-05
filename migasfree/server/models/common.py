# -*- coding: utf-8 -*-

from django.urls import reverse
from django.utils.translation import ugettext
from django.utils.html import format_html
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist

from ..utils import escape_format_string


class MigasLink(object):
    def __init__(self):
        self._actions = None
        self._exclude_links = []
        self._include_links = []

    def get_relations(self):
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
            if obj.remote_field.field.remote_field.parent_link:
                _name = obj.remote_field.field.remote_field.parent_model.__name__.lower()
            else:
                _name = obj.remote_field.field.remote_field.model.__name__.lower()

            if _name == 'attribute':
                if self._meta.model_name == 'computer' and obj.attname == 'tags':
                    _name = 'tag'

            if _name == 'permission':
                break

            count = obj.remote_field.model.objects.filter(
                **{obj.remote_field.name: self.id}
            ).count()
            if count:
                related_link = reverse(
                    u'admin:{}_{}_changelist'.format(
                        obj.remote_field.model._meta.app_label,
                        _name
                    )
                )

                related_data.append({
                    'url': u'{}?{}__id__exact={}'.format(
                        related_link,
                        obj.remote_field.name if _name != 'serverattribute' else 'computer',
                        self.pk
                    ),
                    'text': ugettext(obj.remote_field.field.verbose_name),
                    'count': count
                })

        for related_object, _ in related_objects:
            related_model, _field = self.transmodel(related_object)
            if related_model:
                if not u'{} - {}'.format(
                    related_model._meta.model_name,
                    _field
                ) in self._exclude_links:
                    count = related_model.objects.filter(
                        **{related_object.field.name: self.id}
                    ).count()
                    if count:
                        related_link = reverse(
                            u'admin:{}_{}_changelist'.format(
                                related_model._meta.app_label,
                                related_model.__name__.lower()
                            )
                        )
                        related_data.append({
                            'url': u'{}?{}={}'.format(
                                related_link,
                                _field,
                                self.id
                            ),
                            'text': u'{} [{}]'.format(
                                ugettext(related_model._meta.verbose_name_plural),
                                ugettext(related_object.field.verbose_name)
                            ),
                            'count': count
                        })

        for _include in self._include_links:
            try:
                _model_name, _field_name = _include.split(" - ")
                related_link = reverse(
                    u'admin:{}_{}_changelist'.format(
                        self._meta.app_label,
                        _model_name
                    )
                )
                related_data.append({
                    'url': u'{}?{}__id__exact={}'.format(
                        related_link,
                        _field_name,
                        self.id
                    ),
                    'text': u'{} [{}]'.format(
                        ugettext(_model_name),
                        ugettext(_field_name)
                    )
                })
            except ValueError:
                pass

        return action_data, related_data

    def relations(self):
        action_data = []
        related_data = []

        if self._meta.model_name == 'hwnode':
            related_data.append({
                'url': u'{}?{}={}'.format(
                    reverse('admin:server_computer_changelist'),
                    'product',
                    self.computer.product,
                ),
                'text': u'{} [{}]'.format(
                    ugettext('computer'),
                    ugettext('product')
                )
            })

            return action_data, related_data

        # ATTRIBUTESET === ATTRIBUTE
        if self._meta.model_name == 'attributeset' or (
                (
                    self._meta.model_name == 'attribute' or
                    self._meta.model_name == 'feature'
                ) and self.property_att.prefix == 'SET'
        ):
            if self._meta.model_name == 'attributeset':
                from . import Attribute
                attribute_set = self
                try:
                    att = Attribute.objects.get(
                        value=str(self.name),
                        property_att__prefix='SET'
                    )
                except ObjectDoesNotExist:
                    att = None
            else:
                from . import AttributeSet
                att = self
                try:
                    attribute_set = AttributeSet.objects.get(name=self.value)
                except ObjectDoesNotExist:
                    attribute_set = None

            if att:
                att_action_data, att_related_data = att.get_relations()
            else:
                att_action_data = []
                att_related_data = []

            if attribute_set:
                set_action_data, set_related_data = attribute_set.get_relations()
                action_data = set_action_data + att_action_data
                related_data = set_related_data + att_related_data

            return action_data, related_data

        # COMPUTER === CID ATTRIBUTE
        if self._meta.model_name == 'computer' or (
                (
                    self._meta.model_name == 'attribute' or
                    self._meta.model_name == 'feature'
                ) and self.property_att.prefix == 'CID'
        ):
            if self._meta.model_name == 'computer':
                from . import Attribute
                computer = self
                try:
                    cid = Attribute.objects.get(
                        value=str(self.id),
                        property_att__prefix='CID'
                    )
                except ObjectDoesNotExist:
                    cid = None
            else:
                from . import Computer
                cid = self
                computer = Computer.objects.get(pk=int(self.value))

            computer_action_data, \
                computer_related_data = computer.get_relations()

            if cid:
                cid_action_data, cid_related_data = cid.get_relations()
            else:
                cid_action_data = []
                cid_related_data = []

            action_data = computer_action_data + cid_action_data
            related_data = computer_related_data + cid_related_data

            related_data.append({
                'url': reverse('computer_events', args=(computer.id,)),
                'text': u'{} [{}]'.format(
                    ugettext('Events'),
                    ugettext(computer._meta.model_name)
                )
            })
            related_data.append({
                'url': reverse('computer_simulate_sync', args=(computer.id,)),
                'text': u'{} [{}]'.format(
                    ugettext('Simulate sync'),
                    ugettext(computer._meta.model_name)
                )
            })

            related_data.append({
                'url': reverse('hardware_resume', args=(computer.id,)),
                'text': u'{} [{}]'.format(
                    ugettext('Hardware'),
                    ugettext(computer._meta.model_name)
                )
            })

            related_data.append({
                'url': reverse('computer_label') + '?uuid=' + computer.uuid,
                'text': u'{} [{}]'.format(
                    ugettext('Label'),
                    ugettext(computer._meta.model_name)
                )
            })

            return action_data, related_data
        else:
            return self.get_relations()

    def menu_link(self):
        action_data, related_data = self.relations()

        return render_to_string(
            'includes/migas_link_menu.html',
            {
                'lnk': {
                    'url': reverse(
                        u'admin:{}_{}_change'.format(
                            self._meta.app_label,
                            self._meta.model_name
                        ),
                        args=(self.id,)
                    ),
                    'text': self.__str__(),
                    'actions': action_data,
                    'related': related_data
                }
            }
        )

    def link(self):
        if self._meta.model_name == 'clientattribute' \
                or self._meta.model_name == 'attribute':
            if self.property_att.prefix == 'CID':
                from . import Computer
                try:
                    self = Computer.objects.get(id=self.value)
                except ObjectDoesNotExist:
                    pass
            elif self.property_att.prefix == 'SET':
                from . import AttributeSet
                try:
                    self = AttributeSet.objects.get(name=self.value)
                except ObjectDoesNotExist:
                    pass

        url = u'admin:{}_{}_change'.format(
            self._meta.app_label,
            self._meta.model_name
        )
        if self._meta.model_name == 'attribute':
            if self.property_att.sort == 'server':
                url = u'admin:{}_serverattribute_change'.format(self._meta.app_label)
            else:
                url = u'admin:{}_clientattribute_change'.format(self._meta.app_label)

        lnk = {
            'url': reverse(
                url,
                args=(self.id,)
            ),
            'text': escape_format_string(self.__str__()),
            'app': self._meta.app_label,
            'class': self._meta.model_name,
            'pk': self.id
        }
        if self._meta.model_name == 'computer':
            lnk['status'] = self.status
            lnk['trans_status'] = ugettext(self.status)
        elif self._meta.model_name == 'serverattribute' \
                or (self._meta.model_name == 'attribute' and self.property_att.sort == 'server'):
            lnk['status'] = 'tag'
            lnk['trans_status'] = ugettext(self._meta.verbose_name)
        elif self._meta.model_name == 'attributeset' \
                or (self._meta.model_name in ['clientattribute', 'attribute'] and self.id == 1):
            lnk['status'] = 'set'
            lnk['trans_status'] = ugettext(self._meta.verbose_name)

        return format_html(
            render_to_string(
                'includes/migas_link.html',
                {
                    'lnk': lnk
                }
            )
        )

    link.short_description = '...'

    def transmodel(self, obj):
        from . import ClientAttribute, ServerAttribute, Computer

        if obj.related_model._meta.label_lower == "server.computer" and \
                self.__class__.__name__ in ["ClientAttribute", "Attribute"] and \
                self.property_att.prefix == "CID":
            return Computer, "sync_attributes__id__exact"

        if obj.related_model._meta.label_lower == "server.attribute":
            if self.sort == 'server':
                return ServerAttribute, "Tag"
            else:
                return ClientAttribute, "Attribute"
        elif obj.related_model._meta.label_lower == "server.computer":
            if self.__class__.__name__ == ["ClientAttribute", "Attribute", "ServerAttribute"]:
                if obj.field.related_model._meta.model_name == 'serverattribute':
                    return Computer, "tags__id__exact"
                elif obj.field.related_model._meta.model_name == 'attribute':
                    return Computer, "sync_attributes__id__exact"
        elif obj.related_model._meta.label_lower in [
                "admin.logentry",
                "server.scheduledelay",
                "server.hwnode"
        ]:
            return "", ""  # Excluded

        if obj.field.__class__.__name__ in ['ManyRelatedManager', 'OneToOneField', 'ForeignKey']:
            return obj.related_model, u'{}__id__exact'.format(obj.field.name)
        else:
            return obj.related_model, u"{}__{}__exact".format(
                obj.field.name,
                obj.field.m2m_reverse_target_field_name()
            )
