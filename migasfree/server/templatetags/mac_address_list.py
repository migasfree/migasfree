# -*- coding: utf-8 -*-

from django import template

import re

register = template.Library()

MAC_RAW_LEN = 12


@register.filter(name='mac_address_list')
def mac_address_list(value):
    """
    {{ mac_address|mac_address_list }}
    http://stackoverflow.com/questions/8346735/
    inserting-a-character-at-regular-intervals-in-a-list
    """
    if not value:
        return ''

    ret = []
    for i in range(0, len(value), MAC_RAW_LEN):
        ret.append(':'.join(re.findall('..', value[i:i + MAC_RAW_LEN])))

    return ', '.join(ret)
