# -*- coding: utf-8 -*-

import json

from django import template
from django.contrib.auth.models import User as UserSystem
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe

from ..models import UserProfile

register = template.Library()


class TemplateOrganization(template.Node):
    def render(self, context):
        return settings.MIGASFREE_ORGANIZATION


@register.tag
def organization(parser, token):
    return TemplateOrganization()


class TemplateProject(template.Node):
    def render(self, context):
        try:
            obj = UserProfile.objects.get(id=context["user"].id).project
        except (AttributeError, IndexError, ObjectDoesNotExist):
            obj = ""

        return obj


@register.tag
def project(parser, token):
    return TemplateProject()


class TemplateLink(template.Node):
    def render(self, context):
        try:
            obj = context["original"].link()
        except (AttributeError, IndexError):
            try:
                obj = context["original"].__str__()
            except (AttributeError, IndexError):
                obj = ""

        return obj


@register.tag
def link(parser, token):
    return TemplateLink()


@register.inclusion_tag('admin/submit_line.html', takes_context=True)
def submit_row(context):
    """
    Displays the row of buttons for delete and save.
    We have modified standard submit_row tag for add permissions 'can_save'

    http://stackoverflow.com/questions/9179505/how-to-add-button-to-submit-row-context-in-django
    """

    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    user_id = context['user'].id
    user = UserSystem.objects.get(id=user_id)
    can_save = user.has_perm(
        '{}.can_save_{}'.format(opts.app_label, opts.model_name)
    )

    delete = user.has_perm(
        '{}.delete_{}'.format(opts.app_label, opts.model_name)
    )

    if context['original'] and opts.model_name == "deployment":
        can_save = context['original'].can_save(user)
        delete = context['original'].can_delete(user)

    return {
        'opts': opts,
        'original': context['original'],
        'preserved_filters': context['preserved_filters'],
        'show_delete_link': (
            not is_popup and context['has_delete_permission']
            and (change or context.get('show_delete', True)) and delete
        ),
        'show_save_as_new': not is_popup and change and save_as and can_save,
        'show_save_and_add_another': (
            context['has_add_permission'] and
            not is_popup and (not save_as or context['add'])
            and can_save
        ),
        'show_save_and_continue': not is_popup and context['has_change_permission'] and can_save,
        'is_popup': is_popup,
        'show_save': context['add'] or can_save,
    }


@register.filter
def as_json(data):
    return mark_safe(json.dumps(data))
