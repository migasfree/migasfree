# -*- coding: UTF-8 -*-

import os
import tempfile

from datetime import datetime, timedelta

from django.conf import settings


def writefile(filename, content):
    """
    bool writefile(string filename, string content)
    """

    _file = None
    try:
        _file = open(filename, 'wb')
        _file.write(content)
        _file.flush()
        os.fsync(_file.fileno())
        _file.close()

        return True
    except IOError:
        return False
    finally:
        if _file is not None:
            _file.close()


def readfile(filename):
    with open(filename, 'rb') as fp:
        ret = fp.read()

    return ret


def d2s(dic):
    """Dictionary to String"""
    return ['%s: %s' % (k, v) for (k, v) in list(dic.items())]


def remove_empty_elements_from_dict(dic):
    for (k, v) in list(dic.items()):
        if not v:
            del dic[k]

    return dic


def swap_m2m(source_field, target_field):
    source_m2m = list(source_field.all())
    target_m2m = list(target_field.all())

    source_field.clear()
    source_field.add(*target_m2m)

    target_field.clear()
    target_field.add(*source_m2m)


def horizon(mydate, delay):
    """
    No weekends
    """
    iday = int(mydate.strftime("%w"))
    idelta = delay + (((delay + iday - 1) / 5) * 2)

    return mydate + timedelta(days=idelta)


def percent_horizon(begin_date, end_date):
    delta = end_date - begin_date
    progress = datetime.now().date() - begin_date.date()
    if delta.days > 0:
        percent = float(progress.days + 1) / delta.days * 100
    else:
        percent = 100
    if percent < 0:
        percent = 0
    if percent > 100:
        percent = 100

    return percent


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
    writefile(tmp_file, bash_code)

    os.system("ionice -c 3 bash %(file)s 1> %(file)s.out 2> %(file)s.err" % {
        'file': tmp_file
    })

    out = readfile('%s.out' % tmp_file)
    err = readfile('%s.err' % tmp_file)

    os.remove(tmp_file)
    os.remove('%s.out' % tmp_file)
    os.remove('%s.err' % tmp_file)

    return {"out": out, "err": err}


def get_client_ip(request):
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
