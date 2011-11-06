#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2011 Jose Antonio Chavarría
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Author: Jose Antonio Chavarría <jachavar@gmail.com>

__author__  = 'Jose Antonio Chavarría'
__file__    = 'setup.py'
__date__    = '2011-10-21'
__license__ = 'GPLv3'

# http://guide.python-distribute.org/
# python setup.py --help-commands
# python setup.py build
# python setup.py sdist
# python setup.py bdist --format=rpm

# http://zetcode.com/articles/packageinpython/
# TODO https://wiki.ubuntu.com/PackagingGuide/Python
# TODO https://help.ubuntu.com/community/PythonRecipes/DebianPackage
# TODO https://github.com/astraw/stdeb

import sys

if not hasattr(sys, 'version_info') or sys.version_info < (2, 6, 0, 'final'):
    raise SystemExit('migasfree-client requires Python 2.6 or later.')

import os
README = open(os.path.join(os.path.dirname(__file__), 'README')).read()

#import migasfree
#VERSION = migasfree.__version__
VERSION = '2.1' # migasfree no-trans ;)

import platform
_dist = platform.linux_distribution()
_requires = [
    'python (>=2.6)',
    #'python-ipy', # FIXME
    'curl',
    'createrepo',
    'apache2',
    #'libapache2-mod-wsgi', # FIXME
    #'python-doc-utils', # FIXME
    #'dpkg-dev', # FIXME
]
'''
if _dist[0] == 'Fedora':
    _requires.append('pycurl (>=7.19)') # python-pycurl
elif _dist[0] == 'openSUSE':
    _requires.append('curl (>=7.19)') # python-curl
elif _dist[0] == 'Ubuntu':
    _requires.append('pycurl (>=7.19)')
'''

import glob
import subprocess
from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.log import warn, info, error, fatal
from distutils.dep_util import newer

class InstallData(install_data):
    def run(self):
        self.data_files.extend(self._find_repo_files())
        self.data_files.extend(self._find_other_files())
        self.data_files.extend(self._find_doc_files())
        install_data.run(self)

    def _find_repo_files(self):
        data_files = []

        for root, dirs, files in os.walk('repo'):
            final_files = []
            for archive in files:
                final_files.append(os.path.join(root, archive))

            data_files.append(
                ('/var/%s' % os.path.join('migasfree', root),
                final_files)
            )

        return data_files

    def _find_other_files(self):
        data_files = []

        for directory in ['packages']:
            for root, dirs, files in os.walk(directory):
                final_files = []
                for archive in files:
                    final_files.append(os.path.join(root, archive))

                data_files.append(
                    ('/usr/share/%s' % os.path.join('migasfree-server', root),
                    final_files)
                )

        return data_files

    def _find_doc_files(self):
        data_files = []

        for root, dirs, files in os.walk('doc'):
            # first level does not matter
            if root == 'doc':
                continue

            final_files = []
            for archive in files:
                final_files.append(os.path.join(root, archive))

            # remove doc directory from root
            tmp_dir = root.replace('doc/', '', 1)

            data_files.append(
                ('/usr/share/doc/%s' % os.path.join('migasfree-server', tmp_dir),
                final_files)
            )

        return data_files

setup(
    name         = 'migasfree-server',
    version      = VERSION,
    description  = 'migasfree-server is a Django app to manage systems management',
    long_description = README,
    license      = 'GPLv3',
    author       = 'Alberto Gacías',
    author_email = 'agacias@ono.com',
    url          = 'http://www.migasfree.org/',
    #download_url = 'http://migasfree.org/releases/2.0/migasfree-server-2.0.tar.gz',
    platforms    = ['Linux'],
    packages     = [
        'migasfree',
        'migasfree.middleware',
        'migasfree.server',
        'migasfree.server.templatetags',
    ],
    package_dir  = {
        'migasfree': 'migasfree',
        'migasfree.middleware': 'migasfree/middleware',
        'migasfree.server': 'migasfree/server',
        'migasfree.server.templatetags': 'migasfree/server/templatetags',
    },
    cmdclass     = {
        'install_data': InstallData,
    },
    package_data = {
        'migasfree': [
            'templates/*.html',
            'templates/*/*.html',
            'locale/*/LC_MESSAGES/*.mo',
            'dev-tools/*',
        ],
    },
    data_files   = [
        ('/usr/share/migasfree-server', ['apache/django.wsgi']),
        ('/usr/share/doc/migasfree-server', [
            'AUTHORS',
            'COPYING',
            'INSTALL',
            'MANIFEST.in',
            'README',
        ]),
    ],
    scripts = [
        'bin/migasfree-server-from-scratch',
        'bin/migasfree-server-load-initial-data.py',
        'bin/migasfree-server-import-from-wfe',
    ],
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers  = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    requires = _requires,
)
