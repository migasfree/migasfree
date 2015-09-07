# -*- coding: utf-8 -*-

import json
import time

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core import serializers

from migasfree.server.models import (
    HwNode,
    HwConfiguration,
    HwLogicalName,
    HwCapability,
    Notification,
    Computer
)

MAXINT = 9223372036854775807  # sys.maxint = (2**63) - 1


@login_required
def hardware_resume(request, param):
    computer = get_object_or_404(Computer, id=param)

    hardware = HwNode.objects.filter(computer__id=param).order_by('id')
    data = serializers.serialize('python', hardware)

    return render(
        request,
        'computer_hardware_resume.html',
        {
            'title': '%s: %s' % (_("Hardware Information"), computer),
            'computer': computer,
            'data': data
        }
    )


@login_required
def hardware_extract(request, node):
    node = get_object_or_404(HwNode, id=node)

    capability = HwCapability.objects.filter(node=node.id).values(
        'name', 'description'
    )
    logical_name = HwLogicalName.objects.filter(node=node.id).values('name')
    configuration = HwConfiguration.objects.filter(node=node.id).values(
        'name', 'value'
    )

    return render(
        request,
        'computer_hardware_extract.html',
        {
            'title': '%s: %s' % (_("Hardware Information"), node),
            'computer': node.computer,
            'capability': capability,
            'logical_name': logical_name,
            'configuration': configuration,
        }
    )


def load_hw(computer, node, parent, level):
    n = HwNode()
    n.parent = parent
    n.computer = computer
    n.level = level
    n.name = str(node["id"])
    n.classname = node["class"]
    if "enabled" in node:
        n.enabled = node["enabled"]
    if "claimed" in node:
        n.claimed = node["claimed"]
    if "description" in node:
        n.description = node["description"]
    if "vendor" in node:
        n.vendor = node["vendor"]
    if "product" in node:
        n.product = node["product"]
    if "version" in node:
        n.version = node["version"]
    if "serial" in node:
        n.serial = node["serial"]
    if "businfo" in node:
        n.businfo = node["businfo"]
    if "physid" in node:
        n.physid = node["physid"]
    if "slot" in node:
        n.slot = node["slot"]
    if "size" in node:
        # validate bigint unsigned (#126)
        size = int(node["size"])
        if size <= MAXINT and size >= -MAXINT - 1:
            n.size = size
        else:
            n.size = 0
    if "capacity" in node:
        n.capacity = node["capacity"]
    if "clock" in node:
        n.clock = node["clock"]
    if "width" in node:
        n.width = node["width"]
    if "dev" in node:
        n.dev = node["dev"]

    n.save()
    level += 3

    for e in node:
        if e == "children":
            for x in node[e]:
                load_hw(computer, x, n, level)
        elif e == "capabilities":
            for x in node[e]:
                c = HwCapability()
                c.node = n
                c.name = x
                c.description = node[e][x]
                c.save()
        elif e == "configuration":
            for x in node[e]:
                c = HwConfiguration()
                c.node = n
                c.name = x
                c.value = node[e][x]
                c.save()
        elif e == "logicalname":
            if type(node[e]) == unicode:
                c = HwLogicalName()
                c.node = n
                c.name = node[e]
                c.save()
            else:
                for x in node[e]:
                    c = HwLogicalName()
                    c.node = n
                    c.name = x
                    c.save()
        elif e == "resource":
            print(e, node[e])
        else:
            pass

    return  # ???


def process_hw(computer, jsonfile):
    with open(jsonfile, "r") as f:
        try:
            data = json.load(f)
        except:
            _notification = Notification()
            _notification.notification = \
                "Error: Hardware dictionary is not valid by computer [%s]." % (
                computer.__unicode__()
            )
            _notification.date = time.strftime("%Y-%m-%d %H:%M:%S")
            _notification.save()
            return

    HwNode.objects.filter(computer=computer).delete()
    load_hw(computer, data, None, 1)

    return  # ???
