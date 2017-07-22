# -*- coding: utf-8 -*-

import os
import json
import gpgme

from io import BytesIO
from Crypto.PublicKey import RSA
from django.conf import settings

from . import errmfs
from .utils import read_file, write_file

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


def wrap(filename, data):
    """
    Creates a signed wrapper file around data
    """
    with open(filename, 'wb') as fp:
        json.dump(data, fp)

    sign(filename)

    with open(filename, 'ab') as fp:
        with open("{}.sign".format(filename), "rb") as fpsign:
            fp.write(fpsign.read())

    os.remove("{}.sign".format(filename))


def unwrap(filename, key):
    """
    Returns data inside signed wrapper file
    """
    with open(filename, 'rb') as fp:
        content = fp.read()

    n = len(content)

    write_file("{}.sign".format(filename), content[n - SIGN_LEN:n])
    write_file(filename, content[0:n - SIGN_LEN])

    if verify(filename, key):
        with open(filename, "rb") as f:
            data = json.load(f)
    else:
        data = errmfs.error(errmfs.INVALID_SIGNATURE)

    os.remove("{}.sign".format(filename))

    return data


def check_keys_path():
    if not os.path.lexists(settings.MIGASFREE_KEYS_DIR):
        os.makedirs(settings.MIGASFREE_KEYS_DIR)


def generate_rsa_keys(name='migasfree-server'):
    check_keys_path()

    private_pem = os.path.join(settings.MIGASFREE_KEYS_DIR, '{}.pri'.format(name))
    public_pem = os.path.join(settings.MIGASFREE_KEYS_DIR, '{}.pub'.format(name))

    if not (os.path.exists(private_pem) and os.path.exists(public_pem)):
        key = RSA.generate(2048)
        write_file(public_pem, key.publickey().exportKey('PEM'))
        write_file(private_pem, key.exportKey('PEM'))

        # read only keys
        os.chmod(private_pem, 0o400)
        os.chmod(public_pem, 0o400)


def create_server_keys():
    generate_rsa_keys("migasfree-server")
    generate_rsa_keys("migasfree-packager")
    gpg_get_key("migasfree-repository")


def gpg_get_key(name):
    """
    Returns GPG keys (if not exists it is created)
    """

    gpg_home = os.path.join(settings.MIGASFREE_KEYS_DIR, '.gnupg')
    gpg_conf = os.path.join(gpg_home, 'gpg.conf')
    gpg_agent_conf = os.path.join(gpg_home, 'gpg-agent.conf')
    _file = os.path.join(gpg_home, '{}.gpg'.format(name))

    if not os.path.exists(_file):
        os.environ['GNUPGHOME'] = gpg_home
        if not os.path.exists(gpg_home):
            os.makedirs(gpg_home, 0o700)
            # creates configuration file
            write_file(gpg_conf, 'cert-digest-algo SHA256\ndigest-algo SHA256\nuse-agent\npinentry-mode loopback')
            os.chmod(gpg_conf, 0o600)
            write_file(gpg_agent_conf, 'allow-loopback-pinentry')
            os.chmod(gpg_agent_conf, 0o600)

        key_params = """
Key-Type: RSA
Key-Length: 4096
Name-Real: %s
Name-Email: fun.with@migasfree.org
Expire-Date: 0
"""
        file_params = os.path.join(gpg_home, '{}.txt'.format(name))
        write_file(file_params, key_params % name)

        os.system(
            "echo '' | $(which gpg) --batch "
            "--passphrase-fd 0 --gen-key %(file)s; rm %(file)s" % {
                "file": file_params
            }
        )

        # export and save
        ctx = gpgme.Context()
        ctx.armor = True
        key_data = BytesIO()
        ctx.export(name, key_data)
        write_file(_file, key_data.getvalue())
        os.chmod(_file, 0o600)

    return read_file(_file)


def get_keys_to_client(project):
    """
    Returns the keys for register computer
    """
    if not os.path.exists(
        os.path.join(settings.MIGASFREE_KEYS_DIR, "{}.pri".format(project))
    ):
        generate_rsa_keys(project)

    server_public_key = read_file(os.path.join(
        settings.MIGASFREE_KEYS_DIR,
        settings.MIGASFREE_PUBLIC_KEY
    ))
    project_private_key = read_file(os.path.join(
        settings.MIGASFREE_KEYS_DIR,
        "{}.pri".format(project)
    ))

    return {
        settings.MIGASFREE_PUBLIC_KEY: server_public_key,
        "migasfree-client.pri": project_private_key
    }


def get_keys_to_packager():
    """
    Returns the keys for register packager
    """
    server_public_key = read_file(os.path.join(
        settings.MIGASFREE_KEYS_DIR,
        settings.MIGASFREE_PUBLIC_KEY
    ))
    packager_private_key = read_file(
        os.path.join(
            settings.MIGASFREE_KEYS_DIR,
            settings.MIGASFREE_PACKAGER_PRI_KEY
        )
    )

    return {
        settings.MIGASFREE_PUBLIC_KEY: server_public_key,
        settings.MIGASFREE_PACKAGER_PRI_KEY: packager_private_key
    }
