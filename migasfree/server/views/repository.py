# -*- coding: utf-8 -*-

import os
import time

from django.utils.translation import ugettext as _

from migasfree.settings import MIGASFREE_REPO_DIR
from migasfree.server.models import Version, MessageServer, Package
from migasfree.server.functions import run_in_server


def create_physical_repository(repo, packages_list=None):
    """
    Creates the repository metadata.
    repo = a Repository object
    package_list = a packages_id list (called from RepositoryAdmin.save_model)
    """
    msg = MessageServer()
    msg.text = _("Creating Repositories of %s...") \
        % Version.objects.get(id=repo.version_id).name
    msg.date = time.strftime("%Y-%m-%d %H:%M:%S")
    msg.save()

    def history(repository):
        txt = ""
        pkgs = repository.packages.all()
        for pkg in pkgs:
            txt += " " * 8 + pkg.store.name.ljust(10) + " - " + pkg.name + "\n"

        return txt

    # Get the Package Management System
    o_pms = repo.version.pms
    bash = ""

    txt = _("Analyzing the repositories to create files for version: %s") \
        % repo.version.name + '\n'

    # we remove it
    bash += "rm -rf %s\n" % os.path.join(
        MIGASFREE_REPO_DIR,
        repo.version.name,
        o_pms.slug,
        repo.name
    )

    path_stores = os.path.join(
        MIGASFREE_REPO_DIR,
        repo.version.name,
        'STORES'
    )
    path_tmp = os.path.join(
        MIGASFREE_REPO_DIR,
        repo.version.name,
        'TMP',
        o_pms.slug
    )
    if path_tmp.endswith('/'):
        # remove trailing slash for replacing in template
        path_tmp = path_tmp[:-1]

    bash += "/bin/mkdir -p %s\n" % os.path.join(
        path_tmp,
        repo.name,
        'PKGS'
    )
    txt += "\n    REPOSITORY: %s\n" % repo.name

    if not packages_list is None:
        for id in packages_list:
            package = Package.objects.get(id=id)
            bash += 'ln -sf %s %s\n' % (
                os.path.join(path_stores, package.store.name, package.name),
                os.path.join(path_tmp, repo.name, 'PKGS')
            )
    else:
        for package in repo.packages.all():
            bash += 'ln -sf %s %s\n' % (
                os.path.join(path_stores, package.store.name, package.name),
                os.path.join(path_tmp, repo.name, 'PKGS')
            )

    # We create repository metadata
    cad = o_pms.createrepo
    bash += cad.replace(
        "%REPONAME%", repo.name
    ).replace("%PATH%", path_tmp) + "\n"
    txt += history(repo)

    path_tmp = os.path.join(MIGASFREE_REPO_DIR, repo.version.name, "TMP")
    bash += 'cp -rf %s %s\n' % (
        os.path.join(path_tmp, '*'),
        os.path.join(MIGASFREE_REPO_DIR, repo.version.name)
    )
    bash += "rm -rf %s\n" % path_tmp

    # os.system('echo -e "%s" >> /var/tmp/tmp.txt' % bash)  # DEBUG

    txt_err = run_in_server(bash)["err"]

    msg.delete()

    if not txt_err == "":
        txt += "\n\n*************\n" + txt_err.decode("utf-8")

    return txt
