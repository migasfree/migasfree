import json
from migasfree.system.models import *


def load_HW(computer,node,parent,level):
  n=HW_Node()
  n.parent=parent
  n.computer=computer
  n.level=level
  n.name= str(node["id"])
  n.classname= node["class"]
  if "enabled" in node:
    n.enabled = node["enabled"]
  if "claimed" in node:
    n.claimed = node["claimed"]
  if "description" in node:
    n.description= node["description"]
  if "vendor" in node:
    n.vendor= node["vendor"]
  if "product" in node:
    n.product= node["product"]
  if "version" in node:
    n.version= node["version"]
  if "serial" in node:
    n.serial= node["serial"]
  if "businfo" in node:
    n.businfo= node["businfo"]
  if "physid" in node:
    n.physid= node["physid"]
  if "slot" in node:
    n.slot= node["slot"]
  if "size" in node:
    n.size= int(node["size"])
  if "capacity" in node:
    n.capacity= node["capacity"]
  if "clock" in node:
    n.clock= node["clock"]
  if "width" in node:
    n.width= node["width"]
  if "dev" in node:
    n.dev= node["dev"]

  #set icons

  if not n.product==None:
    if n.classname=="system" and n.product == "VirtualBox ()":
      n.icon="virtualbox.png"

    if n.classname=="system" and n.product == "VMware Virtual Platform ()":
      n.icon="vmplayer.png"

  if not n.businfo==None:
    if n.classname=="processor" and "cpu@" in n.businfo:
      n.icon="cpu.png"

  if n.classname=="display":
    n.icon="display.png"

  if not n.description==None:
#    if n.classname=="system" and n.description.lower() in ["notebook",]:
#      n.icon="laptop.png"

    if n.classname=="memory" and n.description.lower() == "system memory":
      n.icon="memory.png"

    if n.classname=="bus" and n.description.lower() == "motherboard":
      n.icon="motherboard.png"

    if n.classname=="memory" and n.description.lower() == "bios":
      n.icon="chip.png"

    if n.classname=="network" and n.description.lower() == "ethernet interface":
      n.icon="network.png"

    if n.classname=="network" and n.description.lower() == "wireless interface":
      n.icon="radio.png"

    if n.classname=="multimedia" and n.description.lower() in ["audio device","multimedia audio controller", ]:
      n.icon="audio.png"

    if n.classname=="bus" and n.description.lower() == "smbus":
      n.icon="serial.png"

    if n.classname=="bus" and n.description.lower() == "usb controller":
      n.icon="usb.png"


  if not n.name==None:
    if n.classname=="disk" and n.name.lower() == "disk":
      n.icon="disc.png"

    if n.classname=="disk" and n.name.lower() == "cdrom":
      n.icon="cd.png"

    if n.classname=="power" and n.name.lower() == "battery":
      n.icon="battery.png"

    if n.classname=="storage" and n.name.lower() == "scsi":
      n.icon="scsi.png"


  n.save()
  level=level+3

  for e in node: 

    if e=="children":
      for x in node[e]:
        load_HW(computer,x,n,level)

    elif e=="capabilities":
      for x in node[e]:
        c=HW_Capability()
        c.node=n
        c.name=x
        c.description=node[e][x]
        c.save()
      
    elif e=="configuration":
      for x in node[e]:
        c=HW_Configuration()
        c.node=n
        c.name=x
        c.value=node[e][x]
        c.save()

    elif e=="logicalname":
      if type(node[e])==unicode:
            c=HW_LogicalName()
            c.node=n
            c.name=node[e]
            c.save()
      else:
          for x in node[e]:
            c=HW_LogicalName()
            c.node=n
            c.name=x
            c.save()

    elif e=="resource":
      print e, node[e]

    else: 
      pass 

  if n.classname=="system":
    try:
      chassis=HW_Configuration.objects.get(name="chassis",node__id=n.id)
      chassisname=chassis.value.lower()
      if chassisname=="notebook":
        n.icon="laptop.png"

      if chassisname=="low-profile":
        n.icon="desktopcomputer.png"

      if chassisname=="mini-tower":
        n.icon="towercomputer.png"
      n.save()

    except:
      pass

  return
     

def process_HW(computer,jsonfile):
    with open(jsonfile,"r") as f:
        data=json.load(f)

    HW_Node.objects.filter(computer=computer).delete()
    load_HW(computer,data,None,1)
    return
