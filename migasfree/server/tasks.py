# -*- coding: utf-8 -*-

import os
import shutil

from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _

from .functions import run_in_server
from .models import Package, Store


def remove_repository_metadata(request, deploy, old_name=""):
    name = old_name if old_name else deploy.name
    shutil.rmtree(deploy.path(name), ignore_errors=True)

    _msg = ("Deleted repository: %s" % name)
    if hasattr(request, 'META'):
        return messages.add_message(request, messages.SUCCESS, _msg)
    else:
        return _msg


def create_repository_metadata(deploy, packages=None, request=None):
    """
    Creates the repository metadata.
    deploy = a Deployment object
    packages = a id's list of packages
    """
    _tmp_path = deploy.path('TMP')
    _stores_path = Store.path(deploy.project.name, '')[:-1]  # remove trailing slash
    _slug_tmp_path = os.path.join(
        _tmp_path,
        deploy.project.pms.slug
    )

    if _slug_tmp_path.endswith('/'):
        # remove trailing slash for replacing in template
        _slug_tmp_path = _slug_tmp_path[:-1]

    _pkg_tmp_path = os.path.join(
        _slug_tmp_path,
        deploy.name,
        'PKGS'  # FIXME hardcoded path!!!
    )
    if not os.path.exists(_pkg_tmp_path):
        os.makedirs(_pkg_tmp_path)

    _ret = ''
    if not packages and not isinstance(packages, list):
        packages = deploy.packages.all()
    for _pkg in packages:
        if isinstance(_pkg, int):
            _pkg = Package.objects.get(pk=_pkg)
        _dst = os.path.join(_pkg_tmp_path, _pkg.name)
        if not os.path.lexists(_dst):
            os.symlink(
                os.path.join(_stores_path, _pkg.store.name, _pkg.name),
                _dst
            )
            _ret += _('%(package)s in store %(store)s') % \
                {"package": _pkg.name, "store": _pkg.store.name} + '<br />'

    # create metadata
    _run_err = run_in_server(
        deploy.project.pms.createrepo.replace(
            '%REPONAME%', deploy.name
        ).replace('%PATH%', _slug_tmp_path).replace(
            '%KEYS%', settings.MIGASFREE_KEYS_DIR)
    )["err"]

    _source = os.path.join(_slug_tmp_path, deploy.name)

    _target = deploy.path()
    shutil.rmtree(_target, ignore_errors=True)

    shutil.copytree(_source, _target, symlinks=True)
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
