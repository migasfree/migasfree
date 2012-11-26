# -*- coding: utf-8 -*-

import json
import time

#from django.utils.translation import ugettext as _
from django.http import HttpResponse

from migasfree.server.models import *


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
            o_device.values = "_IP='%s'\n_LOCATION='%s'\n" % (
                device["IP"],
                device["location"]
            )
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


def device(request, param):
    t = time.strftime("%Y-%m-%d")

    def downfiledevice(pc, devicename, port):
        o_device = Device.objects.get(name=devicename, connection__name=port)
        fileremote = "http://$MIGASFREE_SERVER/repo/" \
            + str(o_device.model.devicefile.name)
        filelocal = "/tmp/migasfree/" + str(o_device.model.devicefile.name)

        ret = ". /usr/share/migasfree/init\n"

        #PARAMS
        ret += "_NAME=" + name_printer(o_device.model.manufacturer.name, o_device.model.name, o_device.name) + "\n"

        # ret += "_NAME=" + o_device.name + "_" + device.model.name + "\n"
        ret += o_device.values + "\n"

        #Download device file
        ret += "mkdir -p /tmp/migasfree/devices\n"
        ret += "if [ \"$MIGASFREE_PROXY\"=\"\" ]; then\n"
        ret += "    wget --no-cache --no-proxy --header=\"Accept: text/plain;q=0.8\" --header=\"Accept-Language: $MIGASFREE_LANGUAGE\" -dnv \"" + fileremote + "\" -O " + filelocal + " 2>/dev/null\n"
        ret += "else\n"
        ret += "    http_proxy=$MIGASFREE_PROXY\n"
        ret += "    wget --no-cache --header=\"Accept: text/plain;q=0.8\" --header=\"Accept-Language: $MIGASFREE_LANGUAGE\" -dnv \"" + fileremote + "\" -O " + filelocal + " 2>/dev/null\n"
        ret += "fi\n\n"

        #Execute code to add printer
        ret += o_device.render_install()
        #Delete device file
        ret += "rm " + filelocal + "\n"

        # Add the device to computer
        try:
            o_computer = Computer.objects.get(name=pc)
        except:  # si no esta el Equipo lo añadimos
            o_computer = Computer(name=pc)
            o_computer.version = Version.objects.get(id=1)
            o_computer.dateinput = t
            o_computer.save()

        o_computer.devices.add(o_device.id)
        o_computer.save()

        return ret

    def selection(number, title, options):
        if (len(options) <= 1) and (title == "TYPE" or title == "PORT"):
            ret = "_" + title + "=\"" + options[0] + "\"\n"
        else:
            ret = "dialog --backtitle \"migasfree - INSTALL DEVICE " \
                + number + "\" --menu \"" + title + "\" 0 0 0"

            i = 0
            for o in options:
                ret += " \"" + str(i) + "\" \"" + o + "\""
                i += 1

            ret += " 2>/tmp/ans\n"
            ret += "#CANCEL\n"
            ret += "if [ $? = 1 ]\n then\n"
            ret += "   rm -f /tmp/ans\n"
            ret += "   clear\n"
            ret += "   exit 0\n"
            ret += "fi\n"
            ret += "_OPCION=\"`cat /tmp/ans`\"\n"
            ret += "clear\n"

            i = 0
            for o in options:
                ret += "if [ $_OPCION = \"" + str(i) + "\" ] \n  then\n"
                ret += "_" + title + "=\"" + o + "\"\n"
                ret += "fi\n"
                i += 1

        return ret

    def list_type():
        l = []
        types = DeviceType.objects.all()
        for o in types:
            l.append(o.name)
        return l

    def list_manufacturer(devicetype):
        l = []
        manufacturers = DeviceManufacturer.objects.filter(
            devicemodel__devicetype__name=devicetype
        ).distinct()
        for o in manufacturers:
            l.append(o.name)

        return l

    def list_model(devicetype, manufacturer):
        l = []
        o_models = DeviceModel.objects.filter(
            devicetype__name=devicetype, manufacturer__name=manufacturer
        )
        for o in o_models:
            l.append(o.name)

        return l

    def list_port(model):
        l = []
        o_connections = DeviceConnection.objects.filter(devicemodel__name=model)
        for o in o_connections:
            l.append(o.name)

        return l

    def whatdevicetype(number):
        ret = "#!/bin/bash\n"
        ret += "#whatmodel\n"
        ret += ". /usr/share/migasfree/init\n"
        ret += "_FILE_MIGAS=/tmp/install_device_type\n"
        ret += "chmod 700 $_FILE_MIGAS\n"
        ret += "_NUMBER=" + number + "\n"
        ret += selection(number, "TYPE", list_type())
        ret += "download_file \"device/?CMD=install&HOST=$HOSTNAME&TYPE=$_TYPE&NUMBER=$_NUMBER\" \"$_FILE_MIGAS\"\n"

        ret += "if [ $? == 0 ]\n  then\n"
        ret += "   chmod 700 $_FILE_MIGAS\n"
        ret += "   $_FILE_MIGAS\n"
        ret += "fi\n"

        return ret

    def whatdevicemanufacturer(number, devicetype):
        ret = "#!/bin/bash\n"
        ret += "#whatmanufacturer\n"
        ret += ". /usr/share/migasfree/init\n"
        ret += "_FILE_MIGAS=/tmp/install_device_manufacturer\n"
        ret += "chmod 700 $_FILE_MIGAS\n"
        ret += "_NUMBER=" + number + "\n"
        ret += "_TYPE=" + devicetype + "\n"
        ret += selection(number, "MANUFACTURER", list_manufacturer(devicetype))
        ret += "download_file \"device/?CMD=install&HOST=$HOSTNAME&MANUFACTURER=$_MANUFACTURER&TYPE=$_TYPE&NUMBER=$_NUMBER\"  \"$_FILE_MIGAS\"\n"

        ret += "if [ $? == 0 ]\n  then\n"
        ret += "   chmod 700 $_FILE_MIGAS\n"
        ret += "   $_FILE_MIGAS\n"
        ret += "fi\n"

        return ret

    def whatmodel(number, devicetype, manufacturer):
        ret = "#!/bin/bash\n"
        ret += "#whatmodel\n"
        ret += ". /usr/share/migasfree/init\n"
        ret += "_FILE_MIGAS=/tmp/install_device_model\n"
        ret += "chmod 700 $_FILE_MIGAS\n"
        ret += "_NUMBER=" + number + "\n"
        ret += "_TYPE=" + devicetype + "\n"
        ret += "_MANUFACTURER=" + manufacturer + "\n"
        ret += selection(number, "MODEL", list_model(devicetype, manufacturer))
        ret += "download_file \"device/?CMD=install&HOST=$HOSTNAME&MODEL=$_MODEL&MANUFACTURER=$_MANUFACTURER&TYPE=$_TYPE&NUMBER=$_NUMBER\" \"$_FILE_MIGAS\"\n"

        ret += "if [ $? == 0 ]\n  then\n"
        ret += "   chmod 700 $_FILE_MIGAS\n"
        ret += "   $_FILE_MIGAS\n"
        ret += "fi\n"

        return ret

    def whatport(number, devicetype, manufacturer, model):
        ret = "#!/bin/bash\n"
        ret += "#whatport\n"
        ret += ". /usr/share/migasfree/init\n"
        ret += "_FILE_MIGAS=/tmp/install_device_port\n"
        ret += "chmod 700 $_FILE_MIGAS\n"
        ret += "_NUMBER=" + number + "\n"
        ret += "_TYPE=" + devicetype + "\n"
        ret += "_MANUFACTURER=" + manufacturer + "\n"
        ret += "_MODEL=" + model + "\n"
        ret += selection(number, "PORT", list_port(model))
        ret += "download_file \"device/?CMD=install&HOST=$HOSTNAME&MODEL=$_MODEL&MANUFACTURER=$_MANUFACTURER&TYPE=$_TYPE&NUMBER=$_NUMBER&PORT=$_PORT\" \"$_FILE_MIGAS\"\n"

        ret += "if [ $? == 0 ]\n then\n"
        ret += "   chmod 700 $_FILE_MIGAS\n"
        ret += "   $_FILE_MIGAS\n"
        ret += "fi\n"

        return ret

    def processmodel(number, devicetype, manufacturer, model, port):
        ret = "#!/bin/bash\n"
        ret += "#processmodel\n"
        ret += ". /usr/share/migasfree/init\n"
        ret += "_FILE_MIGAS=/tmp/install_device_code\n"
        ret += "_FILE_MIGAS_PARAM=/tmp/install_device_param\n"
        ret += "_FILE_RESP=/tmp/resp\n"

        o_devicemodel = DeviceModel.objects.get(name=model)
        o_deviceconnection = DeviceConnection.objects.get(
            name=port, devicetype__name=devicetype
        )

        fields = o_deviceconnection.fields.split()
        ret += "rm -f $_FILE_MIGAS_PARAM\n"

        ret += "_NAME='" + name_printer(manufacturer, model, number) + "'\n"
        ret += "echo ""_NAME='" + name_printer(manufacturer, model, number) + "'"" >>$_FILE_MIGAS_PARAM\n"
        for f in fields:
            ret += "dialog --backtitle \"migasfree - INSTALL DEVICE " + number + "\" --inputbox \"" + f + "\" 0 0 2>/tmp/ans\n"
            ret += "#CANCEL\n"
            ret += "if [ $? = 1 ]\n  then\n"
            ret += "  rm -f /tmp/ans\n"
            ret += "  clear\n"
            ret += "  exit 0\n"
            ret += "fi\n"
            ret += "_" + f + "=\"`cat /tmp/ans`\"\n"
            ret += "echo \"_" + f + "=\'$_" + f + "\'\" >>$_FILE_MIGAS_PARAM\n"

        #We add the device
        o_device = Device()
        o_device.name = number
        o_device.model = o_devicemodel
        o_device.connection = o_deviceconnection
        o_device.save()

        #Actualize the device
        ret += "upload_file \"$_FILE_MIGAS_PARAM\" directupload/ \"PC=$HOSTNAME;TYPE=" + devicetype + ";NUMBER=" + number + ";MODEL=" + model + ";PORT=" + port + "\"\n"

        ret += "cat > $_FILE_MIGAS << EOF \n"
        ret += ". $_FILE_MIGAS_PARAM\n"
        ret += downfiledevice(host, number, port) + "\n"
        ret += "EOF\n"
        ret += "chmod 700 $_FILE_MIGAS\n"
        ret += "$_FILE_MIGAS\n"

        return ret

    host = request.GET.get('HOST', '')
    number = request.GET.get('NUMBER', '')
    devicetype = request.GET.get('TYPE', '')
    manufacturer = request.GET.get('MANUFACTURER', '')
    model = request.GET.get('MODEL', '')
    port = request.GET.get('PORT', '')
    cmd = request.GET.get('CMD', '')

    if cmd == "install":
        #Reinstall all printer configurated in migasfree
        if number == "ALL":
            cursor = Device.objects.filter(computer__name=host)
            ret = ""
            for c in cursor:
                ret += downfiledevice(host, c.name, c.connection.name)

            return HttpResponse(ret, mimetype="text/plain")

        if port == "":
            cursor = Device.objects.filter(name=number)
        else:
            cursor = Device.objects.filter(name=number, connection__name=port)
            if len(cursor) == 1:
                ret = downfiledevice(host, number, port)

                return HttpResponse(ret, mimetype="text/plain")

        if len(cursor) > 0:  # Si se ha configurado alguna vez el dispositivo
            model = cursor[0].model.name
            deviceconnection = DeviceConnection.objects.filter(devicemodel__name=model)
            if len(deviceconnection) == 1:  # SI el modelo tiene 1 conexion
                ret = downfiledevice(host, number, deviceconnection[0].name)
                return HttpResponse(ret, mimetype="text/plain")
            else:  # SI el modelo no tiene 1 conexion
                if port == "":
                    ret = whatport(
                        number,
                        DeviceModel.objects.get(name=model).devicetype.name,
                        DeviceModel.objects.get(name=model).manufacturer.name,
                        model
                    )
                    return HttpResponse(ret, mimetype="text/plain")
                else:
                    #Existe un device con este port ya configurado?
                    cursor = cursor.filter(connection__name=port)
                    if len(cursor) == 1:
                        ret = downfiledevice(host, number, port)
                        return HttpResponse(ret, mimetype="text/plain")
                    else:
                        ret = processmodel(
                            number,
                            DeviceModel.objects.get(name=model).devicetype.name,
                            DeviceModel.objects.get(name=model).manufacturer.name,
                            model,
                            port
                        )
                        return HttpResponse(ret, mimetype="text/plain")

        else: #si no está el Device lo añadimos
            # Pedimos el device type
            if devicetype == "":
                ret = whatdevicetype(number)
                return HttpResponse(ret, mimetype="text/plain")

            # Pedimos el fabricante
            if manufacturer == "":
                ret = whatdevicemanufacturer(number, devicetype)
                return HttpResponse(ret, mimetype="text/plain")

            # Pedimos el modelo
            if model == "":
                ret = whatmodel(number, devicetype, manufacturer)
                return HttpResponse(ret, mimetype="text/plain")

            # Pedimos el puerto
            if port == "":
                ret = whatport(number, devicetype, manufacturer, model)
                return HttpResponse(ret, mimetype="text/plain")

            # Devolvemos el script para la instalacion
            else:
                ret = processmodel(number, devicetype, manufacturer, model, port)

                return HttpResponse(ret, mimetype="text/plain")
