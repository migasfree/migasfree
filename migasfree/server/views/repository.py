# -*- coding: utf-8 -*-

import os
import time
import shutil

from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _

from migasfree.server.models import Version, MessageServer, Package
from migasfree.server.functions import run_in_server


def create_physical_repository(request, repo):
    """
    Creates the repository metadata.
    repo = a Repository object
    """
    _msg = MessageServer()
    _msg.text = _("Creating repository %s...") % repo.name
    _msg.date = time.strftime("%Y-%m-%d %H:%M:%S")
    _msg.save()

    # first, remove it
    shutil.rmtree(os.path.join(
        settings.MIGASFREE_REPO_DIR,
        repo.version.name,
        repo.version.pms.slug,
        repo.name
    ), ignore_errors=True)

    _path_stores = os.path.join(
        settings.MIGASFREE_REPO_DIR,
        repo.version.name,
        'STORES'
    )
    _path_tmp = os.path.join(
        settings.MIGASFREE_REPO_DIR,
        repo.version.name,
        'TMP',
        repo.version.pms.slug
    )
    if _path_tmp.endswith('/'):
        # remove trailing slash for replacing in template
        _path_tmp = _path_tmp[:-1]

    _pkg_path = os.path.join(
        _path_tmp,
        repo.name,
        'PKGS'
    )
    if not os.path.exists(_pkg_path):
        os.makedirs(_pkg_path)

    for _pkg in repo.packages.all():
        _dst = os.path.join(_path_tmp, repo.name, 'PKGS')
        if not os.path.lexists(_dst):
            os.symlink(
                os.path.join(_path_stores, _pkg.store.name, _pkg.name),
                _dst
            )
            _ret += _('%s in store %s') % (_pkg.name, _pkg.store.name) + '<br />'

    # create metadata
    _run_err = run_in_server(
        repo.version.pms.createrepo.replace(
            '%REPONAME%', repo.name
        ).replace('%PATH%', _path_tmp)
    )["err"]

    _source = os.path.join(
        settings.MIGASFREE_REPO_DIR,
        repo.version.name,
        'TMP'
    )
    _destination = os.path.join(
        settings.MIGASFREE_REPO_DIR,
        repo.version.name
    )
    for _file in os.listdir(_source):
        _src = os.path.join(_source, _file)
        if not os.path.exists(_src):
            shutil.move(_src, _destination)
    shutil.rmtree(_path_tmp)

    _msg.delete()  # end of process -> message server erased

    if _run_err != '':
        return messages.error(request, _run_err.decode("utf-8"))

    return messages.success(request, _('Added packages:') + '<br />' + _ret)
