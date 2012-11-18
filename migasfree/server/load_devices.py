# -*- coding: utf-8 -*-

import json

from datetime import time

from server.models import Device, DeviceType, DeviceModel, DeviceConnection, \
    Computer, Version


def load_devices(jsonfile):
    with open(jsonfile, "r") as f:
        data = json.load(f)

    o_devicetype = DeviceType.objects.get(name="PRINTER")

    for e in data:
        if "Net" in e:
            net = e["Net"]

        if "Local" in e:
            local = e["Local"]

    # NET
    for e in net:
        if "Computers" in e:
            computers = e["Computers"]
        if "Devices" in e:
            devices = e["Devices"]

    #Save Devices
    for device in devices:
        if device != "":
            o_devicemodel = DeviceModel.objects.get(name=device["model"])
            o_deviceconnection = DeviceConnection.objects.get(
                name=device["port"],
                devicetype=o_devicetype
            )

            try:
                # o_device=Device.objects.get(name=device["name"],connection=o_deviceconnection)
                o_device = Device.objects.get(name=device["name"])
            except:
                o_device = Device()

            o_device.name = device["name"]
            o_device.model = o_devicemodel
            o_device.connection = o_deviceconnection
            o_device.values = "_IP='"+device["IP"]+"'\n_LOCATION='"+device["location"]+"'\n"
            o_device.save()

        #Save Computers
        for computer in computers.split(","):
            if computer != "":
                try:
                    o_computer = Computer.objects.get(name=computer)
                except:
                    o_computer = Computer()
                    o_computer.name = computer
                    o_computer.dateinput = time.strftime("%Y-%m-%d")
                    o_computer.version = Version(id=1)
                    o_computer.save()

                o_computer.devices.add(o_device.id)
                o_computer.save()

    # LOCAL
    for e in local:
        o_devicemodel = DeviceModel.objects.get(name=e["model"])
        o_deviceconnection = DeviceConnection.objects.get(
            name=e["port"],
            devicetype=o_devicetype
        )

        try:
            # o_device=Device.objects.get(name=e["name"],connection=o_deviceconnection)
            o_device = Device.objects.get(name=e["name"])
        except:
            o_device = Device()

        o_device.name = e["name"]
        o_device.model = o_devicemodel
        o_device.connection = o_deviceconnection

        o_device.save()

        try:
            o_computer = Computer.objects.get(name=e["computer"])
        except:
            o_computer = Computer()
            o_computer.name = e["computer"]
            o_computer.dateinput = time.strftime("%Y-%m-%d")
            o_computer.version = Version(id=1)
            o_computer.save()

        o_computer.devices.add(o_device.id)
        o_computer.save()

    return ""  # ???
