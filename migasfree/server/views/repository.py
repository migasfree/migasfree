# -*- coding: utf-8 -*-

import os
import time

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from migasfree.settings import MIGASFREE_REPO_DIR
from migasfree.server.models import UserProfile, Version, MessageServer, \
    Repository, Pms
from migasfree.server.functions import run_in_server, compare_values


def create_repositories(version_id):
    """
    Creates the repositories for the version_id, checking the packages field
    changed.
    """
    msg = MessageServer()
    msg.text = _("Creating Repositories of %s...") \
        % Version.objects.get(id=version_id).name
    msg.date = time.strftime("%Y-%m-%d %H:%M:%S")
    msg.save()

    def history(repository):
        txt = ""
        pkgs = repository.packages.all()
        for pkg in pkgs:
            txt += " " * 8 + pkg.store.name.ljust(10) + " - " + pkg.name + "\n"

        return txt

    o_version = Version.objects.get(id=version_id)

    # Get the Package Management System
    o_pms = Pms.objects.get(version=o_version)
    bash = ""

    # Set to True the modified field in the repositories that have been changed
    # yours packages from last time.
    for repo in Repository.objects.filter(version=o_version):
        if compare_values(
            repo.packages.values("id"),
            repo.createpackages.values("id")
        ):
            repo.modified = False
            repo.save()
        else:
            r = Repository.objects.get(id=repo.id)  # FIXME creo que esto sobra
            for pkg in r.createpackages.all():
                r.createpackages.remove(pkg.id)
            for pkg in r.packages.all():
                r.createpackages.add(pkg.id)
            r.modified = True
            r.save()

    # Remove the repositories not active
    for repo in Repository.objects.filter(
        modified=True,
        active=False,
        version=o_version
    ):
        bash += "rm -rf %s\n" % os.path.join(
            MIGASFREE_REPO_DIR,
            repo.version.name,
            o_pms.slug,
            repo.name
        )

    txt = _("Analyzing the repositories to create files for version: %s") \
        % o_version.name + '\n'

    # Loop the Repositories modified and active for this version
    for repo in Repository.objects.filter(
        modified=True,
        active=True,
        version=o_version
    ):
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

    path_tmp = os.path.join(MIGASFREE_REPO_DIR, o_version.name, "TMP")
    bash += 'cp -rf %s %s\n' % (
        os.path.join(path_tmp, '*'),
        os.path.join(MIGASFREE_REPO_DIR, o_version.name)
    )
    bash += "rm -rf %s\n" % path_tmp

    # os.system('echo -e "%s" >> /var/tmp/tmp.txt' % bash)  # DEBUG

    txt_err = run_in_server(bash)["err"]

    msg.delete()

    if not txt_err == "":
        txt += "\n\n****ERROR*****\n" + txt_err

    return txt


@login_required
def create_repos(request):
    """
    Creates the files of repositories in the server
    """
    version = get_object_or_404(UserProfile, id=request.user.id).version

    return render(
        request,
        "info.html",
        {
            "title": _("Create Repositories"),
            "contentpage": create_repositories(version.id),
        }
    )
