# -*- coding: utf-8 -*-

import os

from migasfree.settings import ADMIN_SITE_ROOT_URL

# Programming Language for Properties and FaultDefs
LANGUAGES_CHOICES = (
    (0, 'bash'),
    (1, 'python'),
    (2, 'perl'),
    (3, 'php'),
    (4, 'ruby'),
    (5, 'cmd'),
)


def link(obj, description):
    if obj is None or obj.id is None or obj.id == "":
        return ''
    else:
        return '<a href="%s">%s</a>' % (
            os.path.join(
                ADMIN_SITE_ROOT_URL,
                'server',
                description.lower(),
                str(obj.id)
            ),
            obj.__unicode__()
        )
