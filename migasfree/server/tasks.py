# -*- coding: utf-8 -*-

import os
import shutil

from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _

from .models import Package
from .functions import run_in_server


def remove_physical_repository(request, repo, old_name=""):
    name = old_name if old_name else repo.name
    _destination = os.path.join(
        settings.MIGASFREE_REPO_DIR,
        repo.version.name,
        repo.version.pms.slug,
        name
    )
    shutil.rmtree(_destination, ignore_errors=True)
    _msg = ("Deleted repository: %s" % name)
    if hasattr(request, 'META'):
        return messages.add_message(request, messages.SUCCESS, _msg)
    else:
        return _msg


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
            _ret += _('%(package)s in store %(store)s') % \
                {"package": _pkg.name, "store": _pkg.store.name} + '<br />'

    # create metadata
    _run_err = run_in_server(
        repo.version.pms.createrepo.replace(
            '%REPONAME%', repo.name
        ).replace('%PATH%', _slug_tmp_path).replace(
            '%KEYS%', settings.MIGASFREE_KEYS_DIR)
    )["err"]

    _source = os.path.join(
        _tmp_path,
        repo.version.pms.slug,
        repo.name
    )
    _destination = os.path.join(
        settings.MIGASFREE_REPO_DIR,
        repo.version.name,
        repo.version.pms.slug,
        repo.name
    )
    shutil.rmtree(_destination, ignore_errors=True)
    shutil.copytree(_source, _destination, symlinks=True)
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
