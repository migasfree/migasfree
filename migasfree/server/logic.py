# -*- encoding: utf-8 -*-

import os
import xml.dom.minidom
import time
from datetime import datetime

from django.utils.translation import ugettext as _
from django.db.models import Q
from django.http import HttpResponse

from migasfree.settings import MIGASFREE_REPO_DIR
from migasfree.server.models import *
from migasfree.server.functions import *


def new_attribute(o_login, o_property, par):
    """
    Add a attribute to the system. Par is a "value~name" string or only "valor"
    """
    reg = par.split("~")
    value_att = reg[0].strip()
    if len(reg) > 1:
        description_att = reg[1]
    else:
        description_att = ""

    #Add the atribute
    if value_att != "":
        try:
            o_attribute = Attribute.objects.get(
                value=value_att,
                property_att__id=o_property.id
            )
        except:  # if not exist the attribute, we add it
            if o_property.auto is True:
                o_attribute = Attribute()
                o_attribute.property_att = o_property
                o_attribute.value = value_att
                o_attribute.description = description_att
                o_attribute.save()

    #Add the attribute to Login
    o_login.attributes.add(o_attribute)

    return o_attribute.id


def process_attributes(request, my_file):
    """
    DEPRECATED!!!
    process the file attributes.xml and return a script bash to be execute
    in the client
    """

    t = time.strftime("%Y-%m-%d")
    m = time.strftime("%Y-%m-%d %H:%M:%S")

    ip_adr = request.META['REMOTE_ADDR']

    doc = xml.dom.minidom.parse(my_file)

    dic_computer = {}  # Dictionary of computer
    lst_attributes = []  # List of attributes of computer

    ret = ""

    # Loop the file
    for s in doc.childNodes:
        for n in s.childNodes:
            if n.nodeName == "COMPUTER":
                for e in n.childNodes:
                    if e.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
                        try:
                            dic_computer[e.nodeName] = e.firstChild.data
                        except:
                            pass

                if dic_computer["HOSTNAME"] == "desktop":
                    str_error = _('desktop is not valid name for this computer: IP=%(ip)s') % {'ip': ip_adr}
                    o_error = Error()
                    o_error.computer = Computer.objects.get(name="desktop")
                    o_error.date = m
                    o_error.error = str_error
                    o_error.save()

                    return HttpResponse(
                        "# %s\n" % str_error,
                        mimetype='text/plain'
                    )

                #registration of ip and version of computer
                try:
                    o_computer = Computer.objects.get(name=dic_computer["HOSTNAME"])
                    o_computer.ip = dic_computer["IP"]
                    o_computer.version = Version.objects.get(name=dic_computer["VERSION"])
                    o_computer.save()
                except:  # if not exists the computer, we add it
                    o_computer = Computer(name=dic_computer["HOSTNAME"])
                    o_computer.dateinput = t
                    o_computer.ip = dic_computer["IP"]
                    o_computer.version = Version.objects.get(name=dic_computer["VERSION"])
                    o_computer.save()

                # if not exists the user, we add it
                try:
                    o_user = User.objects.get(name=dic_computer["USER"])
                except:
                    o_user = User()
                    o_user.name = dic_computer["USER"]
                    try:
                        o_user.fullname = dic_computer["USER_FULLNAME"]
                    except:
                        o_user.fullname = ""
                    o_user.save()

                # Save Login
                save_login(dic_computer["HOSTNAME"], dic_computer["USER"])
                o_login = Login.objects.get(
                    computer=Computer.objects.get(
                        name=dic_computer["HOSTNAME"]
                    ), user=User.objects.get(name=dic_computer["USER"])
                )
                o_login.attributes.clear()

                # Get version
                version = dic_computer["VERSION"]

                o_version = Version.objects.get(name=version)

                # Get the Package Management System
                o_pms = Pms.objects.get(id=o_version.pms.id)

            if n.nodeName == "ATTRIBUTES":
                for e in n.childNodes:
                    if e.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:

                        o_property = Property.objects.get(prefix=e.nodeName)
                        try:
                            data = e.firstChild.data

                            # we execute the before_insert function
                            if o_property.before_insert != "":
                                exec(o_property.before_insert.replace("\r", ""))

                                # NORMAL
                            if o_property.kind == "N":
                                lst_attributes.append(new_attribute(o_login, o_property, data))

                            # LIST
                            if o_property.kind == "-":
                                mylist = data.split(",")
                                for element in mylist:
                                    lst_attributes.append(new_attribute(o_login, o_property, element))

                            # ADDS RIGHT
                            if o_property.kind == "R":
                                lista = data.split(".")
                                c = data
                                l = 0
                                for x in lista:
                                    lst_attributes.append(new_attribute(o_login, o_property, c[l:]))
                                    l += len(x) + 1

                            # ADDS LEFT
                            if o_property.kind == "L":
                                lista = data.split(".")
                                c = data
                                l = 0
                                for x in lista:
                                    l += len(x) + 1
                                    lst_attributes.append(new_attribute(o_login, o_property, c[0:l - 1]))

                            # we execute the after_insert function
                            if o_property.after_insert != "":
                                exec(o_property.after_insert.replace("\r", ""))

                        except:
                            pass

            if n.nodeName == "FAULTS":
                for e in n.childNodes:
                    if e.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
                        o_faultdef = FaultDef.objects.get(name=e.nodeName)
                        try:
                            data = e.firstChild.data
                            # we add the fault
                            o_fault = Fault()
                            o_fault.computer = o_computer
                            o_fault.date = m
                            o_fault.text = data
                            o_fault.faultdef = o_faultdef
                            o_fault.save()

                        except:
                            pass

    dic_repos = {}

    repositories = Repository.objects.filter(
        Q(attributes__id__in=lst_attributes), Q(version__id=o_version.id)
    )
    repositories = repositories.filter(Q(version__id=o_version.id), Q(active=True))

    for r in repositories:
        dic_repos[r.name] = r.id

    repositories = Repository.objects.filter(
        Q(schedule__scheduledelay__attributes__id__in=lst_attributes), Q(active=True)
    )
    repositories = repositories.filter(Q(version__id=o_version.id), Q(active=True))
    repositories = repositories.extra(select={'delay': "server_scheduledelay.delay"})

    for r in repositories:
        if horizon(r.date, r.delay) <= datetime.now().date():
            dic_repos[r.name] = r.id

    repositories = Repository.objects.filter(Q(id__in=dic_repos.values()))

    #SCRIPT FOR THE COMPUTER
    ret = "#!/bin/bash\n\n"

    ret += ". /usr/share/migasfree/init\n\n"
    ret += "_FILE_LOG=\"$_DIR_TMP/history_sw.log\"\n"
    ret += "_FILE_ERR=\"$_DIR_TMP/migasfree.err\"\n"
    ret += "_FILE_INV_HW=\"$_DIR_TMP/hardware.json\"\n"

    ret += "\n\n# 1.- PRESERVE INITIAL DATE\n"
    ret += "_INI=`date +'%d-%m-%Y %k:%M:%S'`\n"

    ret += "\n\n# 2.- IF HAVE BEEN INSTALED PACKAGES MANUALITY THE INFORMATION IS UPLOAD TO migasfree server\n"
    ret += "tooltip_status \"" + _("Upload changes of software") + "\"\n"
    ret += "soft_history $_FILE_LOG.1 $_FILE_LOG.0 $_FILE_LOG \"\"\n"

    ret += "\n\n# 3.- If WE HAVE OLD ERRORS, WE UPLOAD ITS TO migasfree SERVER\n"
    ret += "tooltip_status \"" + _("Upload errors") + "\"\n"
    ret += "directupload $_FILE_ERR 2>>$_FILE_ERR\n"

    ret += "\n\n# 4.- SAVE REPOSITORIES\n"
    ret += "tooltip_status \"" + _("Creating Repositories File") + "\"\n"
    ret += save_repositories(repositories, o_version, o_pms)
    ret += "cat $PMS_SOURCES_FILES\n"

    ret += "\n\n# 5.- CLEAN CACHE OF PACKAGE MANAGEMENT SYSTEM\n"
    ret += "tooltip_status \"" + _("Getting data") + "\"\n"
    ret += "pms_cleanall 2>>$_FILE_ERR\n"

    ret += "\n\n# 6.- REMOVE PACKAGES\n"
    ret += "tooltip_status \"" + _("Checking packages to remove") + "\"\n"
    c_packages = ""
    for d in repositories:
        if not d.toremove == "":
            c_packages += " " + d.toremove
    if not c_packages == "":
        ret += "tooltip_status \"" + _("Removing packages") + "\"\n"
        ret += "pms_remove_silent \"" + c_packages.replace("\n"," ") + "\" 2>> $_FILE_ERR\n"

    ret += "\n\n# 7.- INSTALL PACKAGES\n"
    ret += "tooltip_status \"" + _("Checking packages to install") + "\"\n"
    c_packages = ""
    for d in repositories:
        if not d.toinstall == "":
            c_packages += " " + d.toinstall
    if not c_packages == "":
        ret += "tooltip_status \"" + _("Installing packages") + "\"\n"
        ret += "pms_install_silent \"" + c_packages.replace("\n"," ") + "\" 2>> $_FILE_ERR\n"

    ret += "\n\n# 8.- UPDATE PACKAGES\n"
    ret += "tooltip_status \"" + _("Updating packages") + "\"\n"
    ret += "pms_update_silent 2>> $_FILE_ERR\n"

    ret += "\n\n# 9.- UPLOAD THE SOFTWARE HISTORY\n"
    ret += "tooltip_status \"" + _("Upload changes of software") + "\"\n"
    ret += "soft_history $_FILE_LOG.0 $_FILE_LOG.1 $_FILE_LOG \"$_INI\"\n"

    ret += "\n\n# 10.- UPLOAD THE SOFTWARE INVENTORY\n"
    ret += "tooltip_status \"" + _("Upload inventory software") + "\"\n"
    # If is the Computer with de Software Base we upload the list of packages
    if o_version.computerbase == o_computer.name:
        ret += "pms_queryall | sort> $_DIR_TMP/base.log\n"
        ret += "directupload $_DIR_TMP/base.log 2>> $_FILE_ERR\n"
    #Get the software base of the version and upload the diff
    ret += "download_file \"softwarebase/?VERSION=$MIGASFREE_VERSION\" \"$_DIR_TMP/softwarebase.log\" 2>/dev/null\n"
    ret += "soft_inventory $_DIR_TMP/softwarebase.log $_FILE_LOG.1 $_DIR_TMP/software.log\n"

    ret += "\n\n# 11.- UPDATE THE HARDWARE INVENTORY\n"
    ret += "tooltip_status \"" + _("Upload inventory hardware") + "\"\n"

    ret += "_LSHW=`which lshw`\n"
    ret += "if ! [ -z $_LSHW ] ; then\n"

    # BUG in lshw<=2.14 : if exists partitions in ext4 in the computer. We do not get class volume (-c volume)
#    ret = ret+"  $_LSHW -c system -c bus -c memory -c processor -c bridge -c communication -c multimedia -c network -c display -c storage -c disk -c generic -c power > $_FILE_INV_HW\n"

    ret += "  $_LSHW -json > $_FILE_INV_HW\n"
    ret += "  if [ $? = 0 ]; then\n"
    ret += "    directupload $_FILE_INV_HW 2>> $_FILE_ERR\n"
    ret += "  else\n"
    ret += "    echo 'error in lshw version:' >> $_FILE_ERR\n"
    ret += "    $_LSHW -version >> $_FILE_ERR\n"
    ret += "    echo 'migasfree need: lshw >= B.02.15' >> $_FILE_ERR\n"
    ret += "  fi\n"
    ret += "  directupload $_FILE_INV_HW 2>> $_FILE_ERR\n"
    ret += "fi\n"

    ret += "\n\n\n# 12.- UPLOAD ERRORS OF 'migasfree -u' TO migasfree\n"
    ret += "tooltip_status \"" + _("Upload errors") + "\"\n"
    ret += "directupload $_FILE_ERR 2>> $_FILE_ERR\n"

    chk_devices = Mmcheck(o_computer.devices, o_computer.devices_copy)
    if chk_devices.changed() is True or o_computer.devices_modified is True:
        ret += "\n\n\n# 13.- UPDATING DEVICES\n"
        ret += "tooltip_status \"" + _("Updating devices") + "\"\n"

        #remove the devices
        lst_diff = list_difference(s2l(o_computer.devices_copy), s2l(chk_devices.mms()))
        for d in lst_diff:
            try:
                device = Device.objects.get(id=d)
                ret += "_NAME='"+name_printer(device.model.manufacturer.name, device.model.name, device.name)+"'\n"
                ret += device.values + "\n"
                ret += device.render_remove() + "\n"
            except:
                pass

        #install all devices
        ret += "download_file_and_run \"device/?CMD=install&HOST=$HOSTNAME&NUMBER=ALL\" \"$_DIR_TMP/install_device\"\n"

        o_computer.devices_copy = chk_devices.mms()
        o_computer.devices_modified = False
        o_computer.save()

    ret += "tooltip_status \"" + _("System is updated") + "\"\n"
    ret += "icon_status /usr/share/icons/hicolor/48x48/actions/migasfree-ok.png\n"
    ret += "sleep 5\n"

    ret += "tooltip_status \"\"\n"

    return ret


def save_login(pc, user):
    m = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        o_login = Login.objects.get(
            computer=Computer.objects.get(name=pc),
            user=User.objects.get(name=user)
        )
        o_login.date = m
        o_login.save()
    except:  # if Login not exist, we save it
        o_login = Login(
            computer=Computer.objects.get(name=pc),
            user=User.objects.get(name=user)
        )
        o_login.date = m
        o_login.save()

    return  # ???


def save_repositories(lista, o_version, o_pms):
    # Return the content of file of list of repositories
    ret = "cat > $PMS_SOURCES_FILES << EOF\n"

    # Repositories
    for d in lista:
        cad = o_pms.repository + "\n"
        ret += cad.replace("%REPO%", d.name).replace("%VERSION%", o_version.name)

    ret += "EOF\n"

    return ret


def create_repositories_package(packagename, versionname):
    o_version = Version.objects.get(name=versionname)
    try:
        package = Package.objects.get(name=packagename, version=o_version)
        qset = Repository.objects.filter(packages__id=package.id)
        for r in qset:
            for p in r.createpackages.all():
                r.createpackages.remove(p.id)
            r.save()
        create_repositories(package.version.id)
    except:
        pass


def create_repositories(version_id):
    """
    Create the repositories for the version_id, checking the packages field
    changed.
    """
    m = time.strftime("%Y-%m-%d %H:%M:%S")
    msg = MessageServer()
    msg.text = _("Creating Repositories of %s ...") \
        % Version.objects.get(id=version_id).name
    msg.date = m
    msg.save()

    def history(d):
        txt = ""
        pkgs = d.packages.all()
        for o in pkgs:
            txt += "        " + o.store.name.ljust(10) + " - " + o.name + "\n"

        return txt

    o_version = Version.objects.get(id=version_id)

    #Get the Package Management System
    o_pms = Pms.objects.get(version=o_version)
    bash = ""

    # Set to True the modified field in the repositories that have been change
    # yours packages from last time.
    dset = Repository.objects.filter(version=o_version)
    for d in dset:
        if compare_values(d.packages.values("id"), d.createpackages.values("id")):
            d.modified = False
            d.save()
        else:
            r = Repository.objects.get(id=d.id)
            for p in r.createpackages.all():
                r.createpackages.remove(p.id)
            for p in r.packages.all():
                r.createpackages.add(p.id)
            r.modified = True
            r.save()

    #Remove the repositories not active
    dset = Repository.objects.filter(
        modified=True,
        active=False,
        version=o_version
    )
    for d in dset:
        bash += "rm -rf %s\n" % os.path.join(
            MIGASFREE_REPO_DIR,
            d.version.name,
            o_pms.slug,
            d.name
        )

    #Loop the Repositories modified and active for this version
    dset = Repository.objects.filter(
        modified=True,
        active=True,
        version=o_version
    )
    for d in dset:
        # we remove it
        bash += "rm -rf %s\n" % os.path.join(
            MIGASFREE_REPO_DIR,
            d.version.name,
            o_pms.slug,
            d.name
        )

    txt = "Analyzing the repositories to create files for version: %s\n" \
        % o_version.name

    for d in dset:
        path_stores = os.path.join(
            MIGASFREE_REPO_DIR,
            d.version.name,
            'STORES'
        )
        path_tmp = os.path.join(
            MIGASFREE_REPO_DIR,
            d.version.name,
            'TMP',
            o_pms.slug
        )
        if path_tmp.endswith('/'):
            # remove trailing slash for replacing in template
            path_tmp = path_tmp[:-1]

        bash += "/bin/mkdir -p %s\n" % os.path.join(path_tmp, d.name, 'PKGS')
        txt += "\n    REPOSITORY: %s\n" % d.name
        for p in d.packages.all():
            bash += 'ln -s %s %s\n' % (
                os.path.join(path_stores, p.store.name, p.name),
                os.path.join(path_tmp, d.name, 'PKGS')
            )

        # We create the metadata of repository
        cad = o_pms.createrepo

        bash += cad.replace("%REPONAME%", d.name).replace("%PATH%", path_tmp) + "\n"
        txt += history(d)

    path_tmp = os.path.join(MIGASFREE_REPO_DIR, o_version.name, "TMP")
    bash += 'cp -rf %s %s\n' % (
        os.path.join(path_tmp, '*'),
        os.path.join(MIGASFREE_REPO_DIR, o_version.name)
    )
    bash += "rm -rf %s\n" % path_tmp

    # os.system('echo -e "%s" >> /var/tmp/tmp.txt' % bash)  # DEBUG

    txt_err = run_in_server(bash)["err"]

    msg.delete()

    if not txt_err == "":
        txt += "\n\n****ERROR*****\n" + txt_err

    return txt


def name_printer(manufacturer, model, number):  # TODO to devices.py
    return '%s-%s_[%s]' % (manufacturer, model, number)
