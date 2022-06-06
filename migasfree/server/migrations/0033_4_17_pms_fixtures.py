# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0032_4_17_migasfree_play_fixtures'),
    ]

    operations = [
        migrations.RunSQL(
            [(
                "UPDATE server_pms SET createrepo=%s WHERE id=1 AND name='yum';",
                [
                    "_DIR=%PATH%/%REPONAME%\nrm -rf $_DIR/repodata\nrm -rf $_DIR/checksum\ncreaterepo -c checksum $_DIR\ngpg -u migasfree-repository --homedir %KEYS%/.gnupg --detach-sign --armor $_DIR/repodata/repomd.xml\n",
                ]
            )],
            [(
                "UPDATE server_pms SET createrepo=%s WHERE id=1 AND name='yum';",
                [
                    "_DIR=%PATH%/%REPONAME%\nrm -rf $_DIR/repodata\nrm -rf $_DIR/checksum\ncreaterepo -c checksum $_DIR\n",
                ]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_pms SET createrepo=%s WHERE id=2 AND name='zypper';",
                [
                    "_DIR=%PATH%/%REPONAME%\nrm -rf $_DIR/repodata\nrm -rf $_DIR/checksum\ncreaterepo -c checksum $_DIR\ngpg -u migasfree-repository --homedir %KEYS%/.gnupg --detach-sign --armor $_DIR/repodata/repomd.xml\n",
                ]
            )],
            [(
                "UPDATE server_pms SET createrepo=%s WHERE id=2 AND name='zypper';",
                [
                    "_DIR=%PATH%/%REPONAME%\nrm -rf $_DIR/repodata\nrm -rf $_DIR/checksum\ncreaterepo -c checksum $_DIR\n",
                ]
            )]
        ),
    ]
