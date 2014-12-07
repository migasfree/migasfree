# -*- coding: utf-8 -*-

import os
import json
import gpgme
from io import BytesIO

import migasfree.server.errmfs as errmfs

from django.conf import settings

from migasfree.server.functions import readfile, writefile

SIGN_LEN = 256


def sign(filename):
    os.system("openssl dgst -sha1 -sign %s -out %s %s" % (
        os.path.join(settings.MIGASFREE_KEYS_DIR, 'migasfree-server.pri'),
        "%s.sign" % filename,
        filename
    ))


def verify(filename, key):
    return os.system(
        "openssl dgst -sha1 -verify %s -signature %s %s 1>/dev/null" %
        (
            os.path.join(settings.MIGASFREE_KEYS_DIR, '%s.pub' % key),
            "%s.sign" % filename,
            filename
        )
    ) == 0  # returns True if OK, False otherwise


def check_keys_path():
    if not os.path.lexists(settings.MIGASFREE_KEYS_DIR):
        os.makedirs(settings.MIGASFREE_KEYS_DIR)


def gen_keys(name):
    """
    Generates a pair of RSA keys
    """
    check_keys_path()

    private_key = os.path.join(settings.MIGASFREE_KEYS_DIR, "%s.pri" % name)
    public_key = os.path.join(settings.MIGASFREE_KEYS_DIR, "%s.pub" % name)

    os.system("openssl genrsa -out %s 2048" % private_key)
    os.system("openssl rsa -in %s -pubout > %s" % (private_key, public_key))

    # read only keys
    os.chmod(private_key, 0o400)
    os.chmod(public_key, 0o400)


def gpg_get_key(name):
    """
    Return keys gpg and if not exists it is created
    """

    gpghome = os.path.join(settings.MIGASFREE_KEYS_DIR, ".gnupg")
    _file = os.path.join(gpghome, name + ".gpg")

    if not os.path.exists(_file):
        os.environ['GNUPGHOME'] = gpghome
        if not os.path.exists(gpghome):
            os.mkdir(gpghome, 0o700)
            # create a blank configuration file
            with open(os.path.join(gpghome, 'gpg.conf'), 'wb') as handle:
                handle.write('')
            #os.chmod(os.path.join(gpghome, 'gpg.conf'), 0o600)

        # create a context
        ctx = gpgme.Context()

        key_params = """
<GnupgKeyParms format="internal">
Key-Type: RSA
Key-Length: 4096
Name-Real: %s
Expire-Date: 0
</GnupgKeyParms>
"""
        ctx.genkey(key_params % name)

        # export and save
        ctx.armor = True
        keydata = BytesIO()
        ctx.export(name, keydata)
        _key = keydata.getvalue()
        with open(_file, 'wb') as handle:
            handle.write(_key)

    with open(_file, 'rb') as handle:
        _key = handle.read()

    return _key


def get_keys_to_client(version):
    """
    Returns the keys for register computer
    """
    if not os.path.exists(
        os.path.join(settings.MIGASFREE_KEYS_DIR, "%s.pri" % version)
    ):
        gen_keys(version)

    server_public_key = readfile(os.path.join(
        settings.MIGASFREE_KEYS_DIR,
        "migasfree-server.pub"
    ))
    version_private_key = readfile(os.path.join(
        settings.MIGASFREE_KEYS_DIR,
        "%s.pri" % version
    ))

    return {
        "migasfree-server.pub": server_public_key,
        "migasfree-client.pri": version_private_key
    }


def get_keys_to_packager():
    """
    Returns the keys for register packager
    """
    server_public_key = readfile(os.path.join(
        settings.MIGASFREE_KEYS_DIR,
        "migasfree-server.pub"
    ))
    packager_private_key = readfile(
        os.path.join(settings.MIGASFREE_KEYS_DIR, "migasfree-packager.pri")
    )

    return {
        "migasfree-server.pub": server_public_key,
        "migasfree-packager.pri": packager_private_key
    }


def create_keys_server():
    gen_keys("migasfree-server")
    gen_keys("migasfree-packager")
    gpg_get_key("migasfree-repository")


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

    writefile("%s.sign" % filename, content[n - SIGN_LEN:n])
    writefile(filename, content[0:n - SIGN_LEN])

    if verify(filename, key):
        with open(filename, "rb") as f:
            data = json.load(f)
    else:
        data = errmfs.error(errmfs.SIGNNOTOK)  # Sign not OK

    os.remove("%s.sign" % filename)

    return data
