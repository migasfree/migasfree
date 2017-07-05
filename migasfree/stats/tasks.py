# -*- coding: UTF-8 -*-

import os

from datetime import datetime, timedelta

from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models import (
    Error, Fault, Message,
    Notification, Package, Project,
)


def orphan_packages():
    """
    Packages that have not been assigned to any deployment
    """
    return {
        'msg': _('Orphan Package/Set'),
        'target': 'server',
        'level': 'warning',
        'result': Package.orphan_count(),
        'url': reverse('admin:server_package_changelist') + '?deployment__isnull=True',
    }


def unchecked_notifications():
    """
    Server Notifications that must be checked
    """
    return {
        'msg': _('Unchecked Notificacions'),
        'target': 'server',
        'level': 'warning',
        'result': Notification.unchecked_count(),
        'url': reverse('admin:server_notification_changelist') + '?checked__exact=0',
    }


def unchecked_faults(user_id=0):
    """
    You must check fault when the it is solved
    """
    url = reverse('admin:server_fault_changelist') + '?checked__exact=0'
    if user_id:
        url += '&user=me'

    return {
        'msg': _('Unchecked Faults'),
        'target': 'computer',
        'level': 'danger',
        'result': Fault.unchecked_count(user_id),
        'url': url,
    }


def unchecked_errors():
    """
    You must check error when it is solved
    """
    return {
        'msg': _('Unchecked Errors'),
        'target': 'computer',
        'level': 'danger',
        'result': Error.unchecked_count(),
        'url': reverse('admin:server_error_changelist') + '?checked__exact=0',
    }


def synchronizing_computers():
    """
    How many computers are being synchronized at this time
    """
    t = datetime.now() - timedelta(seconds=settings.MIGASFREE_SECONDS_MESSAGE_ALERT)

    return {
        'msg': _('Synchronizing Computers'),
        'target': 'computer',
        'level': 'info',
        'result': Message.objects.filter(updated_at__gt=t).count(),
        'url': reverse('computer_messages'),
    }


def delayed_computers():
    """
    How many computers are delayed
    """
    t = datetime.now() - timedelta(seconds=settings.MIGASFREE_SECONDS_MESSAGE_ALERT)

    return {
        'msg': _('Delayed Computers'),
        'target': 'computer',
        'level': 'warning',
        'result': Message.objects.filter(updated_at__lt=t).count(),
        # 'url': reverse('computer_messages'),
        'url': reverse('admin:server_message_changelist')
               + '?updated_at__lt=' + t.strftime("%Y-%m-%d %H:%M:%S")
    }


def generating_repositories():
    result = 0
    msg = ''
    if os.path.exists(settings.MIGASFREE_PUBLIC_DIR):
        for item in os.listdir(settings.MIGASFREE_PUBLIC_DIR):
            project = Project.objects.filter(name=item)
            if project:
                project = project[0]
                repos = os.path.join(
                    settings.MIGASFREE_PUBLIC_DIR,
                    project.name,
                    'TMP',  # FIXME hardcoded string!!!
                    project.pms.slug
                )
                if os.path.exists(repos):
                    for repo in os.listdir(repos):
                        result += 1
                        msg += _('%s at %s.') % (repo, project.name)

    msg = _('Generating %s repositories: %s') % (result, msg)

    return {
        'msg': msg,
        'target': 'server',
        'level': 'info',
        'result': result,
        'url': '#',
    }


def checkings(user_id=0):
    """
    Returns checkings results order by level ('info', 'warning', 'error')
    """
    return [
        generating_repositories(),
        synchronizing_computers(),
        orphan_packages(),
        unchecked_notifications(),
        delayed_computers(),
        unchecked_faults(user_id),
        unchecked_errors(),
    ]
