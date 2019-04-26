# -*- coding: utf-8 -*-

import json

from django.urls import reverse
from django.utils.translation import ugettext
from django.utils.html import format_html
from django.utils.http import urlencode
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from ..utils import escape_format_string


class MigasLink(object):
    PROTOCOL = "mea"

    def __init__(self):
        self._actions = None
        self._exclude_links = []
        self._include_links = []

    @staticmethod
    def related_title(related_objects):
        if related_objects:
            first = related_objects[0]
            if related_objects.count() == 1:
                return first._meta.verbose_name

            return first._meta.verbose_name_plural

        return ""

    @staticmethod
    def get_description(action):
        if "description" in action:
            return action["description"]

        return ""

    def is_related(self, action):
        model = self._meta.model_name.lower()
        if "related" in action:

            # COMPUTER === CID ATTRIBUTE
            if self._meta.model_name == 'computer' or (
                        (
                         self._meta.model_name in ['attribute','clientattribute']
                        ) and self.property_att.prefix == 'CID'
            ):
                model = "computer"

            # ATTRIBUTE SET === ATTRIBUTE
            elif self._meta.model_name == 'attributeset' \
                    or (self._meta.model_name == 'attribute' and self.pk > 1) \
                    and self.property_att.prefix == 'SET':
                model = "attributeset"

            # DOMAIN === ATTRIBUTE
            elif self._meta.model_name == 'domain' or \
                    (self._meta.model_name in ['attribute', 'serverattribute'] and self.property_att.prefix == 'DMN'):
                model = "domain"

        return "related" not in action or model in action["related"]

    def get_relations(self, request):
        user = request.user.userprofile
        server = request.META.get('HTTP_HOST')

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

        actions = []
        data = []
        if self._actions is not None and any(self._actions):
            for item in self._actions:
                actions.append({
                    "url": item[1],
                    "title": item[0],
                    "description": item[2] if len(item) == 3 else "",
                })

        if self._meta.model_name.lower() in settings.MIGASFREE_EXTERNAL_ACTIONS:
            element = settings.MIGASFREE_EXTERNAL_ACTIONS[self._meta.model_name.lower()]
            for action in element:
                if self.is_related(element[action]):
                    action_info = {
                            "name": action,
                            "model": self._meta.model_name,
                            'id': self.id,
                            "related_model": self._meta.model_name,
                            "related_ids": [self.id],
                            "server": server
                        }

                    actions.append({
                        "url": "{}://{}".format(self.PROTOCOL, json.dumps(action_info)),
                        "title": element[action]["title"],
                        "description": self.get_description(element[action]),
                    })

        data.append({
            'url': reverse(
                u'admin:{}_{}_changelist'.format(
                    self._meta.app_label,
                    self._meta.model_name
                )
            ) + str(self.id),
            'text': u"{} {}".format(self._meta.verbose_name, self.__str__()),
            'count': 1,
            'actions': actions
        })

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

            if hasattr(obj.remote_field.model.objects, 'scope'):
                rel_objects = obj.remote_field.model.objects.scope(user).filter(
                    **{obj.remote_field.name: self.id}
                )
            else:
                rel_objects = obj.remote_field.model.objects.filter(
                    **{obj.remote_field.name: self.id}
                )
            count = rel_objects.count()

            if count:
                related_link = reverse(
                    u'admin:{}_{}_changelist'.format(
                        obj.remote_field.model._meta.app_label,
                        _name
                    )
                )

                actions = []
                if _name in settings.MIGASFREE_EXTERNAL_ACTIONS:
                    element = settings.MIGASFREE_EXTERNAL_ACTIONS[_name]
                    for action in element:
                        if "many" not in element[action] or element[action]["many"] or count == 1:
                            if self.is_related(element[action]):
                                info_action = {
                                    "name": action,
                                    "model": self._meta.model_name,
                                    'id': self.id,
                                    "related_model": _name,
                                    "related_ids": list(rel_objects.values_list("id", flat=True)),
                                    "server": server,
                                }

                                actions.append({
                                    "url": "{}://{}".format(self.PROTOCOL, json.dumps(info_action)),
                                    "title": element[action]["title"],
                                    "description": self.get_description(element[action]),
                                })

                data.append({
                    'url': u'{}?{}__id__exact={}'.format(
                        related_link,
                        obj.remote_field.name if _name != 'serverattribute' else 'computer',
                        self.pk
                    ),
                    'text': ugettext(obj.remote_field.field.verbose_name),
                    'count': count,
                    'actions': actions
                })

        for related_object, _ in related_objects:
            related_model, _field = self.transmodel(related_object)
            if related_model:
                # EXCLUDE CID
                if related_model.__name__.lower() != "computer" or not (
                        self._meta.model_name == "attribute" and self.property_att.prefix == 'CID'
                ):
                    if not u'{} - {}'.format(
                        related_model._meta.model_name,
                        _field
                    ) in self._exclude_links:

                        if hasattr(related_model.objects, 'scope'):
                            if related_model.__name__.lower() == "computer":
                                rel_objects = related_model.productive.scope(user).filter(
                                    **{related_object.field.name: self.id}
                                )
                            else:
                                rel_objects = related_model.objects.scope(user).filter(
                                    **{related_object.field.name: self.id}
                                )
                        else:
                            rel_objects = related_model.objects.filter(
                                **{related_object.field.name: self.id}
                            )

                        count = rel_objects.count()
                        if count:
                            related_link = reverse(
                                u'admin:{}_{}_changelist'.format(
                                    related_model._meta.app_label,
                                    related_model.__name__.lower()
                                )
                            )

                            actions = []
                            if related_model.__name__.lower() in settings.MIGASFREE_EXTERNAL_ACTIONS:
                                element = settings.MIGASFREE_EXTERNAL_ACTIONS[related_model.__name__.lower()]
                                for action in element:
                                    if "many" not in element[action] or element[action]["many"] or count == 1:
                                        if self.is_related(element[action]):
                                            info_action = {
                                                "name": action,
                                                "model": self._meta.model_name,
                                                'id': self.id,
                                                "related_model": related_model.__name__.lower(),
                                                "related_ids": list(rel_objects.values_list("id", flat=True)),
                                                "server": server,
                                            }

                                            actions.append({
                                                "url": "{}://{}".format(self.PROTOCOL, json.dumps(info_action)),
                                                "title": element[action]["title"],
                                                "description": self.get_description(element[action]),
                                            })

                            if related_model.__name__.lower() == "computer":
                                data.append({
                                    'url': u'{}?{}={}&status__in=intended,reserved,unknown'.format(
                                        related_link,
                                        _field,
                                        self.id
                                    ),
                                    'text': u'{} [{}]'.format(
                                        ugettext(related_model._meta.verbose_name_plural),
                                        ugettext(related_object.field.verbose_name)
                                    ),
                                    'count': count,
                                    'actions': actions
                                })
                            else:
                                data.append({
                                    'url': u'{}?{}={}'.format(
                                        related_link,
                                        _field,
                                        self.id
                                    ),
                                    'text': u'{} [{}]'.format(
                                        ugettext(related_model._meta.verbose_name_plural),
                                        ugettext(related_object.field.verbose_name)
                                    ),
                                    'count': count,
                                    'actions': actions
                                })

        # SPECIAL RELATIONS (model must have a method named: 'related_objects').
        actions = []
        if self._meta.model_name.lower() in [
            'device', 'deployment', 'scope', 'domain', 'attributeset', 'faultdefinition', 'platform'
        ]:
            rel_objects = self.related_objects("computer", user)
            if rel_objects.exists():
                if "computer" in settings.MIGASFREE_EXTERNAL_ACTIONS:
                    element = settings.MIGASFREE_EXTERNAL_ACTIONS["computer"]
                    for action in element:
                        if "many" not in element[action] or element[action]["many"] or rel_objects.count() == 1:
                            if self.is_related(element[action]):
                                info_action = {
                                    "name": action,
                                    "model": self._meta.model_name,
                                    'id': self.id,
                                    "related_model": "computer",
                                    "related_ids": list(rel_objects.values_list("id", flat=True)),
                                    "server": server,
                                }

                                actions.append({
                                    "url": "{}://{}".format(self.PROTOCOL, json.dumps(info_action)),
                                    "title": element[action]["title"],
                                    "description": self.get_description(element[action]),
                                })

                    if self._meta.model_name.lower() == 'platform':
                        data.append({
                            'url': u'{}?{}={}'.format(
                                '/admin/server/{}/'.format('computer'),
                                'project__platform__id__exact',
                                str(self.id)
                            ),
                            'text': u'{}'.format(ugettext(self.related_title(rel_objects))),
                            'count': rel_objects.count(),
                            'actions': actions
                        })
                    elif self._meta.model_name.lower() == 'device':
                        from .attribute import Attribute
                        data.append({
                            'url': u'{}?{}={}&status__in=intended,reserved,unknown'.format(
                                '/admin/server/{}/'.format('computer'),
                                'sync_attributes__id__in',
                                str(list(
                                    Attribute.objects.scope(
                                        request.user.userprofile
                                    ).filter(
                                        devicelogical__device__id=self.id
                                    ).values_list("id", flat=True)
                                )).replace(" ", "").replace("[", "").replace("]", "")
                            ),
                            'text': u'{}'.format(ugettext(self.related_title(rel_objects))),
                            'count': rel_objects.count(),
                            'actions': actions
                        })
                    else:
                        data.append({
                            'url': u'{}?{}={}'.format(
                                '/admin/server/{}/'.format('computer'),
                                'id__in',
                                str(list(
                                    rel_objects.values_list("id", flat=True)
                                )).replace(" ", "").replace("[", "").replace("]", "")
                            ),
                            'text': u'{}'.format(ugettext(self.related_title(rel_objects))),
                            'count': rel_objects.count(),
                            'actions': actions
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
                data.append({
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

        return data

    def relations(self, request):
        data = []

        if self._meta.model_name == 'hwnode':
            from . import Computer
            data.append({
                'url': u'{}?{}'.format(
                    reverse('admin:server_computer_changelist'),
                    urlencode({'product': self.computer.product}),
                ),
                'text': u'{} [{}]'.format(
                    ugettext('computer'),
                    ugettext('product')
                ),
                'count': Computer.productive.scope(request.user.userprofile).filter(
                    product=self.computer.product
                ).count()
            })

            return data

        # DOMAIN === ATTRIBUTE
        if self._meta.model_name == 'domain' or (
                self._meta.model_name == 'serverattribute' and self.property_att.prefix == 'DMN'
        ):
            if self._meta.model_name == 'domain':
                from . import Attribute
                domain = self
                try:
                    att = Attribute.objects.get(
                        value=str(self.name),
                        property_att__prefix='DMN'
                    )
                except ObjectDoesNotExist:
                    att = None
            else:
                from . import Domain
                att = self
                try:
                    domain = Domain.objects.get(name=self.value)
                except ObjectDoesNotExist:
                    domain = None
            if att:
                att_data = att.get_relations(request)
            else:
                att_data = []

            if domain:
                set_data = domain.get_relations(request)
                data = set_data + att_data

            return data

        # ATTRIBUTE SET === ATTRIBUTE
        if self._meta.model_name == 'attributeset' \
                or (self._meta.model_name == 'attribute' and self.pk > 1) \
                and self.property_att.prefix == 'SET':
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
                att_data = att.get_relations(request)
            else:
                att_data = []

            if attribute_set:
                set_data = attribute_set.get_relations(request)
                data = set_data + att_data

            return data

        # COMPUTER === CID ATTRIBUTE
        if self._meta.model_name == 'computer' or (
                (
                    self._meta.model_name == 'attribute' or
                    self._meta.model_name == 'clientattribute'
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

            computer_data = computer.get_relations(request)

            if cid:
                cid_data = cid.get_relations(request)
            else:
                cid_data = []

            data = computer_data + cid_data

            return data
        else:
            return self.get_relations(request)

    def menu_link(self, request):
        data = self.relations(request)

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
                    'related': data
                }
            }
        )

    def badge(self):
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
            elif self.property_att.prefix == 'DMN':
                from . import Domain
                try:
                    self = Domain.objects.get(name=self.value)
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

        if self._meta.model_name == 'deployment':
            from . import Deployment
            if self.source == Deployment.SOURCE_INTERNAL:
                url = u'admin:{}_internalsource_change'.format(self._meta.app_label)
            elif self.source == Deployment.SOURCE_EXTERNAL:
                url = u'admin:{}_externalsource_change'.format(self._meta.app_label)

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
            lnk['trans_status'] = u'{}, {}, {}, {}'.format(
                ugettext(self.status),
                self.project,
                self.ip_address,
                self.sync_user
            )
        elif self._meta.model_name == 'domain':
            lnk['status'] = 'domain'
            lnk['trans_status'] = ugettext(self._meta.verbose_name)
        elif self._meta.model_name == 'serverattribute' \
                or (self._meta.model_name == 'attribute' and self.property_att.sort == 'server'):
            lnk['status'] = 'tag'
            lnk['trans_status'] = ugettext(self._meta.verbose_name)
        elif self._meta.model_name == 'attributeset' \
                or (self._meta.model_name in ['clientattribute', 'attribute'] and self.id == 1):
            lnk['status'] = 'set'
            lnk['trans_status'] = ugettext(self._meta.verbose_name)
        elif self._meta.model_name == 'policy':
            lnk['status'] = 'policy'
            lnk['trans_status'] = ugettext(self._meta.verbose_name)

        return lnk

    def link(self):
        return format_html(
            render_to_string(
                'includes/migas_link.html',
                {'lnk': self.badge()}
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
