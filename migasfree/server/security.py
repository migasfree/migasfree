# -*- coding: utf-8 -*-

import os
import json

from migasfree.server.functions import writefile
from migasfree.server.functions import readfile

import migasfree.server.errmfs as errmfs

from migasfree.settings import MIGASFREE_KEYS_DIR


def sign(filename):
    os.system("openssl dgst -sha1 -sign %s -out %s %s" % (
        os.path.join(MIGASFREE_KEYS_DIR, 'migasfree-server.pri'),
        "%s.sign" % filename,
        filename
    ))


def verify(filename, key):
    return os.system(
        "openssl dgst -sha1 -verify %s -signature %s %s 1>/dev/null" %
        (
            os.path.join(MIGASFREE_KEYS_DIR, '%s.pub' % key),
            "%s.sign" % filename,
            filename
        )
    ) == 0  # returns True if OK, False otherwise


def gen_keys(version):
    """
    Generates a pair of RSA keys
    """
    # Private Key
    os.system("openssl genrsa -out %s 2048"
        % os.path.join(MIGASFREE_KEYS_DIR, "%s.pri" % version)
    )

    # Public Key
    os.system("openssl rsa -in %s -pubout > %s" % (
        os.path.join(MIGASFREE_KEYS_DIR, "%s.pri" % version),
        os.path.join(MIGASFREE_KEYS_DIR, "%s.pub" % version)
    ))

    # read only keys
    os.chmod(os.path.join(MIGASFREE_KEYS_DIR, "%s.pri" % version), 0o400)
    os.chmod(os.path.join(MIGASFREE_KEYS_DIR, "%s.pub" % version), 0o400)


def get_keys_to_client(version):
    """
    Returns the keys for register computer
    """
    if not os.path.exists(
        os.path.join(MIGASFREE_KEYS_DIR, "%s.pri" % version)
    ):
        gen_keys(version)

    server = readfile(os.path.join(MIGASFREE_KEYS_DIR, "migasfree-server.pub"))
    client = readfile(os.path.join(MIGASFREE_KEYS_DIR, "%s.pri" % version))

    return {
        "migasfree-server.pub": server,
        "migasfree-client.pri": client
    }


def get_keys_to_packager():
    """
    Returns the keys for register packager
    """
    server = readfile(os.path.join(MIGASFREE_KEYS_DIR, "migasfree-server.pub"))
    packager = readfile(
        os.path.join(MIGASFREE_KEYS_DIR, "migasfree-packager.pri")
    )

    return {
        "migasfree-server.pub": server,
        "migasfree-packager.pri": packager
    }


def create_keys_server():
    if not os.path.lexists(MIGASFREE_KEYS_DIR):
        os.makedirs(MIGASFREE_KEYS_DIR)

    gen_keys("migasfree-server")
    gen_keys("migasfree-packager")


def wrap(filename, data):
    """
    Creates a signed wrapper file around data
    """
    with open(filename, 'wb') as fp:
        json.dump(data, fp)

    sign(filename)

    with open(filename, 'ab') as fp:
        with open("%s.sign" % filename, "rb") as fpsign:
            fp.write(fpsign.read())

    os.remove("%s.sign" % filename)


def unwrap(filename, key):
    """
    Returns data inside signed wrapper file
    """
    with open(filename, 'rb') as fp:
        content = fp.read()

    n = len(content)

    writefile("%s.sign" % filename, content[n - 256:n])
    writefile(filename, content[0:n - 256])

    if verify(filename, key):
        with open(filename, "rb") as f:
            data = json.load(f)
    else:
        data = errmfs.error(errmfs.SIGNNOTOK)  # Sign not OK

    os.remove("%s.sign" % filename)

    return data
