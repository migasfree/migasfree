# -*- coding: utf-8 -*-

# https://djangosnippets.org/snippets/1866/

from django import template

register = template.Library()

def sizify(value):
    """
    Simple kb/mb/gb size snippet for templates:

    {{ product.file.size|sizify }}
    """

    if value < 512000:
        value = value / 1024.0
        ext = 'KB'
    elif value < 4194304000:
        value = value / 1048576.0
        ext = 'MB'
    else:
        value = value / 1073741824.0
        ext = 'GB'
    return '%s %s' % (str(round(value, 2)), ext)

register.filter('sizify', sizify)
