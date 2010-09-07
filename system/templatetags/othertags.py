from django import template
from migasfree.system.logic import getVariable
from migasfree.system.models import UserVersion
from migasfree.system.models import UserProfile
from migasfree.system.models import Version
from django.contrib.auth.models import User as UserSystem

register = template.Library()


class TemplateVariable(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        return getVariable(self.var_name)

class TemplateVersion(template.Node):
    def render(self, context):
        user_id=context["user"].id
        try:
            obj=UserProfile.objects.get(id=user_id).version.name
        except:
            obj=""
        return obj

@register.tag
def organization(parser, token):    
    """
    Return the variable 'ORGANIZATION'.
    """
    return TemplateVariable("ORGANIZATION")
organization=register.tag(organization)


@register.tag
def version(parser, token):    
    """
    Return the version name of user.
    """
    return TemplateVersion()
version=register.tag(version)




# Modified for add permissions "can_save"
def submit_row(context):
    """
    Displays the row of buttons for delete and save. 
    We have modified standard submit_row tag for add permissions 'can_save'
    """
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']

    user_id=context["user"].id
    can_save=UserSystem.objects.get(id=user_id).has_perm("system.can_save_"+opts.module_name)

    return {
        'onclick_attrib': (opts.get_ordered_objects() and change
                            and 'onclick="submitOrderForm();"' or ''),
        'show_delete_link': (not is_popup and context['has_delete_permission']
                              and (change or context['show_delete'])),
        'show_save_as_new': not is_popup and change and save_as and can_save,
        'show_save_and_add_another': context['has_add_permission'] and 
                            not is_popup and (not save_as or context['add']) and can_save,
        'show_save_and_continue': not is_popup and context['has_change_permission'] and can_save,
        'is_popup': is_popup,
        'show_save': context['add'] or (can_save),

    }
submit_row = register.inclusion_tag('admin/submit_line.html', takes_context=True)(submit_row)




#def admin_media_prefix():
#    """
#    Returns the string contained in the setting ADMIN_MEDIA_PREFIX.
#    """
#    try:
#        from django.conf import settings
#    except ImportError:
#        return ''
#    return iri_to_uri(settings.ADMIN_MEDIA_PREFIX)
#admin_media_prefix = register.simple_tag(admin_media_prefix)
