# -*- coding: utf-8 -*-

import os
import time
import shutil

from django.conf import settings
from django.utils.translation import ugettext as _

from migasfree.server.models import Version, MessageServer, Package
from migasfree.server.functions import run_in_server


# FIXME this is not a view (move to another location)
def create_physical_repository(repo, packages=None):
    """
    Creates the repository metadata.
    repo = a Repository object
    packages = a packages_id list (called from RepositoryAdmin.save_model)
    """
    _msg = MessageServer()
    _msg.text = _("Creating Repositories of %s...") \
        % Version.objects.get(id=repo.version_id).name
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

    _ret = _('Added packages:') + '<br />'
    if packages is not None:
        for _pkg_id in packages:
            _pkg = Package.objects.get(id=_pkg_id)
            _dst = os.path.join(_path_tmp, repo.name, 'PKGS')
            if not os.path.lexists(_dst):
                os.symlink(
                    os.path.join(_path_stores, _pkg.store.name, _pkg.name),
                    _dst
                )
                _ret += _('%s in store %s') % (_pkg.name, _pkg.store.name) \
                    + '<br />'
    else:
        for _pkg in repo.packages.all():
            _dst = os.path.join(_path_tmp, repo.name, 'PKGS')
            if not os.path.lexists(_dst):
                os.symlink(
                    os.path.join(_path_stores, _pkg.store.name, _pkg.name),
                    _dst
                )
                _ret += _('%s in store %s') % (_pkg.name, _pkg.store.name) \
                    + '<br />'

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
        _ret += '<br /><br />*************' + _run_err.decode("utf-8")

    return _ret
