# -*- coding: utf-8 -*-

import os
import time
import shutil

from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _

from migasfree.server.models import Version, Package
from migasfree.server.functions import run_in_server


def create_physical_repository(request, repo, packages):
    """
    Creates the repository metadata.
    repo = a Repository object
    packages = a packages_id list
    """
    _tmp_path = os.path.join(
        settings.MIGASFREE_REPO_DIR,
        repo.version.name,
        'TMP'
    )
    _stores_path = os.path.join(
        settings.MIGASFREE_REPO_DIR,
        repo.version.name,
        'STORES'
    )
    _slug_tmp_path = os.path.join(
        settings.MIGASFREE_REPO_DIR,
        repo.version.name,
        'TMP',
        repo.version.pms.slug
    )

    if _slug_tmp_path.endswith('/'):
        # remove trailing slash for replacing in template
        _slug_tmp_path = _slug_tmp_path[:-1]

    _pkg_tmp_path = os.path.join(
        _slug_tmp_path,
        repo.name,
        'PKGS'
    )
    if not os.path.exists(_pkg_tmp_path):
        os.makedirs(_pkg_tmp_path)

    _ret = ''
    for _pkg_id in packages:
        _pkg = Package.objects.get(id=_pkg_id)
        _dst = os.path.join(_slug_tmp_path, repo.name, 'PKGS', _pkg.name)
        if not os.path.lexists(_dst):
            os.symlink(
                os.path.join(_stores_path, _pkg.store.name, _pkg.name),
                _dst
            )
            _ret += _('%s in store %s') % (_pkg.name, _pkg.store.name) + '<br />'

    # create metadata
    _run_err = run_in_server(
        repo.version.pms.createrepo.replace(
            '%REPONAME%', repo.name
        ).replace('%PATH%', _slug_tmp_path)
    )["err"]

    # remove original repository before move temporal
    shutil.rmtree(os.path.join(
        settings.MIGASFREE_REPO_DIR,
        repo.version.name,
        repo.version.pms.slug,
        repo.name
    ), ignore_errors=True)

    # move temporal contents to original repository
    _source = os.path.join(
        _tmp_path,
        'REPOSITORIES'
    )
    _destination = os.path.join(
        settings.MIGASFREE_REPO_DIR,
        repo.version.name,
        'REPOSITORIES'
    )
    for src_dir, dirs, files in os.walk(_source):
        dst_dir = src_dir.replace(_source, _destination)
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.move(src_file, dst_dir)
    shutil.rmtree(_tmp_path)

    if _run_err != '':
        _msg_level = messages.ERROR
        _ret = _run_err.decode("utf-8")
    else:
        _msg_level = messages.SUCCESS
        _ret = _('Added packages:') + '<br />' + _ret

    if hasattr(request, 'META'):
        return messages.add_message(request, _msg_level, _ret)
    else:
        return _ret
