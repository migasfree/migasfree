# -*- coding: utf-8 -*-

import os
import json

from migasfree.server.functions import writefile
from migasfree.server.functions import readfile

import migasfree.server.errmfs as errmfs

from migasfree.settings import MIGASFREE_APP_DIR

_PATH_KEYS = os.path.join(MIGASFREE_APP_DIR, 'keys')

def sign(filename):
    os.system("openssl dgst -sha1 -sign %s -out %s %s" % (
        os.path.join(_PATH_KEYS, 'migasfree-server.pri'),
        "%s.sign" % filename,
        filename
    ))

def verify(filename, key):
    if os.system("openssl dgst -sha1 -verify %s -signature %s %s 1>/dev/null" % (
        os.path.join(_PATH_KEYS, '%s.pub' % key),
        "%s.sign" % filename,
        filename
    )):
        return False
    else:
        return True

def gen_keys(version):
    """
    Generate a pair of keys RSA
    """
    # Private Key
    os.system("openssl genrsa -out %s 2048" % os.path.join(_PATH_KEYS, "%s.pri" % version))

    # Public Key
    os.system("openssl rsa -in %s -pubout > %s" % (
        os.path.join(_PATH_KEYS, "%s.pri" % version),
        os.path.join(_PATH_KEYS, "%s.pub" % version)
    ))

    # read only keys
    os.system("chmod 400 %s" % os.path.join(_PATH_KEYS, "%s.*" % version))

def get_keys_to_client(version):
    """
    Get the keys for register computer
    """
    if not os.path.exists(os.path.join(_PATH_KEYS, "%s.pri" % version)):
        gen_keys(version)

    server = readfile(os.path.join(_PATH_KEYS, "migasfree-server.pub"))
    client = readfile(os.path.join(_PATH_KEYS, "%s.pri" % version))

    return {
        "migasfree-server.pub": server,
        "migasfree-client.pri": client
    }

# Get the keys for register packager
def get_keys_to_packager():
    server = readfile(os.path.join(_PATH_KEYS, "migasfree-server.pub"))
    packager = readfile(os.path.join(_PATH_KEYS, "migasfree-packager.pri"))

    return {
        "migasfree-server.pub": server,
        "migasfree-packager.pri": packager
    }

def create_keys_server():
    if not os.path.lexists(_PATH_KEYS):
        os.mkdir(_PATH_KEYS)
        gen_keys("migasfree-server")
        gen_keys("migasfree-packager")

def wrap(filename, data):
    """
    Dado el data crea el fichero envoltorio con firma
    """
    fp = open(filename, 'wb')
    json.dump(data, fp)
    fp.close()

    sign(filename)

    fp = open(filename, 'ab')
    fpsign = open("%s.sign" % filename,"rb")
    fp.write(fpsign.read())
    fpsign.close()
    fp.close()

    os.remove("%s.sign" % filename)

def unwrap(filename, key):
    """
    Dado el fichero envoltorio con firma devuelve el data
    """
    fp = open(filename, 'rb')
    content = fp.read()
    fp.close()

    n = len(content)

    writefile("%s.sign" % filename, content[n-256:n])
    writefile(filename, content[0:n-256])

    if verify(filename, key):
        with open(filename, "rb") as f:
            data = json.load(f)
        f.close()
    else:
        data = errmfs.error(errmfs.SIGNNOTOK) # Sign not OK

    os.remove("%s.sign" % filename)

    return data
