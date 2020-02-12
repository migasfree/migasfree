# -*- coding: UTF-8 -*-

import os
import tempfile
import copy

from datetime import datetime, timedelta

from django.conf import settings
from django.utils.html import format_html


def write_file(filename, content):
    """
    bool write_file(string filename, string content)
    """

    _file = None
    try:
        _file = open(filename, 'wb')
        try:
            _file.write(bytes(content))
        except TypeError:
            _file.write(bytes(content, encoding='utf8'))
        _file.flush()
        os.fsync(_file.fileno())
        _file.close()

        return True
    except IOError:
        return False
    finally:
        if _file is not None:
            _file.close()


def read_file(filename):
    with open(filename, 'rb') as fp:
        ret = fp.read()

    return ret


def d2s(dic):
    """Dictionary to String"""
    return ['{}: {}'.format(k, v) for (k, v) in list(dic.items())]


def compare_list_values(l1, l2):
    """ returns True if both list are equal """
    if len(l1) != len(l2):
        return False

    l1_set = set(l1)

    return l1_set & set(l2) == l1_set


def list_difference(l1, l2):
    """ uses l1 as reference, returns list of items not in l2 """
    return list(set(l1).difference(l2))


def list_common(l1, l2):
    """ uses l1 as reference, returns list of items in l2 """
    return list(set(l1).intersection(l2))


def run_in_server(bash_code):
    _, tmp_file = tempfile.mkstemp()
    write_file(tmp_file, bash_code)

    os.system("ionice -c 3 bash %(file)s 1> %(file)s.out 2> %(file)s.err" % {
        'file': tmp_file
    })

    out = read_file('{}.out'.format(tmp_file))
    err = read_file('{}.err'.format(tmp_file))

    os.remove(tmp_file)
    os.remove('{}.out'.format(tmp_file))
    os.remove('{}.err'.format(tmp_file))

    return {"out": out, "err": err}


def get_client_ip(request):
    # http://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
    ip = request.META.get('REMOTE_ADDR')

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]

    return ip


def uuid_validate(uuid):
    if len(uuid) == 32:
        uuid = "%s-%s-%s-%s-%s" % (
            uuid[0:8],
            uuid[8:12],
            uuid[12:16],
            uuid[16:20],
            uuid[20:32]
        )

    if uuid in settings.MIGASFREE_INVALID_UUID:
        return ""
    else:
        return uuid


def uuid_change_format(uuid):
    """
    change to big-endian or little-endian format
    """
    if len(uuid) == 36:
        return "%s%s%s%s-%s%s-%s%s-%s-%s" % (
            uuid[6:8],
            uuid[4:6],
            uuid[2:4],
            uuid[0:2],
            uuid[11:13],
            uuid[9:11],
            uuid[16:18],
            uuid[14:16],
            uuid[19:23],
            uuid[24:36]
        )

    return uuid


def time_horizon(date, delay):
    """
    No weekends
    """
    weekday = int(date.strftime("%w"))  # [0(Sunday), 6]
    delta = delay + (((delay + weekday - 1) / 5) * 2)

    return date + timedelta(days=delta)


def swap_m2m(source_field, target_field):
    source_m2m = list(source_field.all())
    target_m2m = list(target_field.all())

    source_field.clear()
    source_field.add(*target_m2m)

    target_field.clear()
    target_field.add(*source_m2m)


def remove_empty_elements_from_dict(dic):
    return dict((k, v) for k, v in dic.items() if v)


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def to_timestamp(dt, epoch=datetime(1970, 1, 1)):
    td = dt.replace(tzinfo=None) - epoch

    return td.total_seconds()


def to_heatmap(results, range_name='day'):
    """
    :param results: [{"day": datetime, "count": int}, ...]
    :param range_name
    :return: {"timestamp": int, ...}
    """

    heatmap = dict()
    for item in results:
        heatmap[str(to_timestamp(item[range_name]))] = item['count']

    return heatmap


def remove_duplicates_preserving_order(seq):
    seen = set()
    seen_add = seen.add

    return [x for x in seq if not (x in seen or seen_add(x))]


def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)

    return fmt.format(**d)


def escape_format_string(text):
    return text.replace('{', '{{').replace('}', '}}')


def to_list(text):
    """
    Converts text with new lines and spaces to list (space delimiter)
    """
    return text.replace('\r', ' ').replace('\n', ' ').split() if text else []


def html_label(count, title='', link='#', level='default'):
    if not count:
        return format_html(
            '<span class="label label-default" title="{}">{}</span>'.format(
                title,
                count
            )
        )

    return format_html(
        '<a class="label label-{}" title="{}" href="{}">{}</a>'.format(
            level,
            title,
            link,
            count
        )
    )


def sort_depends(data):
    # if something fails, ask @agacias
    ret = []
    data_copy = copy.deepcopy(data)

    def sort():
        for i, s in list(data_copy.items()):
            if not s:
                if data_copy:
                    ret.append(i)
                    del data_copy[i]
                    for _, n in list(data_copy.items()):
                        if i in n:
                            n.remove(i)

                    sort()

        if data_copy:
            raise ValueError(data_copy)
        else:
            return ret

    return sort()
