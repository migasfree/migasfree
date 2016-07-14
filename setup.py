#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2011-2016 Jose Antonio Chavarría <jachavar@gmail.com>
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

__author__ = 'Jose Antonio Chavarría'
__license__ = 'GPLv3'

# http://guide.python-distribute.org/
# python setup.py --help-commands
# python setup.py build
# python setup.py sdist
# python setup.py bdist --format=rpm
# python setup.py --command-packages=stdeb.command bdist_deb (python-stdeb)

# http://zetcode.com/articles/packageinpython/
# TODO https://wiki.ubuntu.com/PackagingGuide/Python
# TODO https://help.ubuntu.com/community/PythonRecipes/DebianPackage

import sys

if not hasattr(sys, 'version_info') or sys.version_info < (2, 7, 0, 'final'):
    raise SystemExit('migasfree-server requires Python 2.7 or later.')

import os
PATH = os.path.dirname(__file__)
README = open(os.path.join(PATH, 'README.md')).read()
VERSION = __import__('migasfree').__version__

from distutils.core import setup
from distutils.command.install_data import install_data


class InstallData(install_data):
    def _find_repo_files(self):
        data_files = []

        for root, _, files in os.walk('repo'):
            if 'source' in root:
                continue  # exclude SVG files
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
            for root, _, files in os.walk(directory):
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

        for root, _, files in os.walk('doc'):
            # first level does not matter
            if root == 'doc':
                continue

            final_files = []
            for archive in files:
                final_files.append(os.path.join(root, archive))

            # remove doc directory from root
            tmp_dir = root.replace('doc/', '', 1)

            data_files.append(
                (
                    '/usr/share/doc/%s' % os.path.join(
                        'migasfree-server',
                        tmp_dir
                    ),
                    final_files
                )
            )

        return data_files

    def run(self):
        self.data_files.extend(self._find_repo_files())
        self.data_files.extend(self._find_other_files())
        self.data_files.extend(self._find_doc_files())
        install_data.run(self)

setup(
    name='migasfree-server',
    version=VERSION,
    description='migasfree-server is a Django app to manage systems management',
    long_description=README,
    license='GPLv3',
    author='Alberto Gacías',
    author_email='alberto@migasfree.org',
    url='http://www.migasfree.org/',
    platforms=['Linux'],
    packages=[
        'migasfree',
        'migasfree.middleware',
        'migasfree.server',
        'migasfree.server.admin',
        'migasfree.server.migrations',
        'migasfree.server.models',
        'migasfree.server.templatetags',
        'migasfree.server.views',
        'migasfree.settings',
    ],
    package_dir={
        'migasfree': 'migasfree',
        'migasfree.middleware': 'migasfree/middleware',
        'migasfree.server': 'migasfree/server',
        'migasfree.server.admin': 'migasfree/server/admin',
        'migasfree.server.migrations': 'migasfree/server/migrations',
        'migasfree.server.models': 'migasfree/server/models',
        'migasfree.server.templatetags': 'migasfree/server/templatetags',
        'migasfree.server.views': 'migasfree/server/views',
    },
    cmdclass={
        'install_data': InstallData,
    },
    package_data={
        'migasfree': [
            'locale/*/LC_MESSAGES/*.mo',
            'server/fixtures/*',
            'server/static/ajax-select/*.css',
            'server/static/ajax-select/images/*',
            'server/static/css/*',
            'server/static/img/*',
            'server/static/js/*',
            'server/static/fonts/*',
            'server/templates/*.html',
            'server/templates/*/*.html',
            'server/templates/*/*/*.html',
        ],
    },
    data_files=[
        ('/usr/share/doc/migasfree-server', [
            'AUTHORS',
            'COPYING',
            'INSTALL',
            'MANIFEST.in',
            'README.md',
        ]),
        ('/usr/share/migasfree-server/setup', [
            'setup/common.sh',
            'setup/db_server.sh',
            'setup/web_server.sh',
            'setup/from_scratch.sh',
        ]),
    ],
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
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
)
