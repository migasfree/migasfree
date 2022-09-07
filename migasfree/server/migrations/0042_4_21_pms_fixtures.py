# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0041_4_20_pms_fixtures'),
    ]

    operations = [
        migrations.RunSQL(
            [(
                "UPDATE server_pms SET createrepo=%s WHERE id=3 AND name='apt-get';",
                [
                    "_NAME=%REPONAME%\n_ARCHS=(\"i386 amd64 source\")\nfor _ARCH in ${_ARCHS[@]}\ndo\n  cd %PATH%\n  mkdir -p $_NAME/PKGS/binary-$_ARCH/\n  cd ..\n\n  ionice -c 3 apt-ftparchive --arch $_ARCH packages . > dists/$_NAME/PKGS/binary-$_ARCH/Packages 2> /tmp/$_NAME\n  if [ $? != 0 ]\n  then\n    (>&2 cat /tmp/$_NAME)\n  fi\n  sed -i \"s/Filename: .*\\/PKGS\\//Filename: dists\\/$_NAME\\/PKGS\\//\" dists/$_NAME/PKGS/binary-$_ARCH/Packages\n    sed -i \"s/Filename: .*\\/STORES\\/[^/]*\\//Filename: dists\\/$_NAME\\/PKGS\\//\" dists/$_NAME/PKGS/binary-$_ARCH/Packages\n  gzip -9c dists/$_NAME/PKGS/binary-$_ARCH/Packages > dists/$_NAME/PKGS/binary-$_ARCH/Packages.gz\ndone\n\nfunction calculate_hash {\n  echo $1\n  _FILES=$(find  -type f | sed 's/^.\\///' | sort)\n  for _FILE in $_FILES\n  do\n    _SIZE=$(printf \"%16d\\n\" $(ls -l $_FILE | cut -d ' ' -f5))\n    _HASH=$($2 $_FILE | cut -d ' ' -f1) $()\n    echo \" $_HASH\" \"$_SIZE\" \"$_FILE\"\n  done\n}\n\nfunction create_deploy {\n  _F=\"$(mktemp /var/tmp/deploy-XXXXX)\"\n\n  rm Release 2>/dev/null || :\n  rm Release.gpg 2>/dev/null || :\n  touch Release\n  rm $_F 2>/dev/null || :\n\n  echo \"Architectures: ${_ARCHS[@]}\" > $_F\n  echo \"Codename: $_NAME\" >> $_F\n  echo \"Components: PKGS\" >> $_F\n  echo \"Date: $(date -u '+%a, %d %b %Y %H:%M:%S UTC')\" >> $_F\n  echo \"Label: migasfree $_NAME repository\" >> $_F\n  echo \"Origin: migasfree\" >> $_F\n  echo \"Suite: $_NAME\" >> $_F\n\n  calculate_hash \"MD5Sum:\" \"md5sum\" >> $_F\n  calculate_hash \"SHA1:\" \"sha1sum\" >> $_F\n  calculate_hash \"SHA256:\" \"sha256sum\" >> $_F\n  calculate_hash \"SHA512:\" \"sha512sum\" >> $_F\n\n  mv $_F Release\n\n  gpg -u migasfree-repository --homedir %KEYS%/.gnupg --clearsign -o InRelease Release\n  gpg -u migasfree-repository --homedir %KEYS%/.gnupg -abs -o Release.gpg Release\n}\n\ncd dists/$_NAME\ncreate_deploy\n",
                ]
            )],
            [(
                "UPDATE server_pms SET createrepo=%s WHERE id=3 AND name='apt-get';",
                [
                    "_NAME=%REPONAME%\n_ARCHS=(\"i386 amd64 source\")\nfor _ARCH in ${_ARCHS[@]}\ndo\n  cd %PATH%\n  mkdir -p $_NAME/PKGS/binary-$_ARCH/\n  cd ..\n\n  ionice -c 3 apt-ftparchive --arch $_ARCH packages . > dists/$_NAME/PKGS/binary-$_ARCH/Packages 2> /tmp/$_NAME\n  sed -i \"s/Filename: \\.\\//Filename: /g\" dists/$_NAME/PKGS/binary-$_ARCH/Packages\n  if [ $? != 0 ]\n  then\n    (>&2 cat /tmp/$_NAME)\n  fi\n  gzip -9c dists/$_NAME/PKGS/binary-$_ARCH/Packages > dists/$_NAME/PKGS/binary-$_ARCH/Packages.gz\ndone\n\nfunction calculate_hash {\n  echo $1\n  _FILES=$(find  -type f | sed 's/^.\\///' | sort)\n  for _FILE in $_FILES\n  do\n    _SIZE=$(printf \"%16d\\n\" $(ls -l $_FILE | cut -d ' ' -f5))\n    _HASH=$($2 $_FILE | cut -d ' ' -f1) $()\n    echo \" $_HASH\" \"$_SIZE\" \"$_FILE\"\n  done\n}\n\nfunction create_deploy {\n  _F=\"$(mktemp /var/tmp/deploy-XXXXX)\"\n\n  rm Release 2>/dev/null || :\n  rm Release.gpg 2>/dev/null || :\n  touch Release\n  rm $_F 2>/dev/null || :\n\n  echo \"Architectures: ${_ARCHS[@]}\" > $_F\n  echo \"Codename: $_NAME\" >> $_F\n  echo \"Components: PKGS\" >> $_F\n  echo \"Date: $(date -u '+%a, %d %b %Y %H:%M:%S UTC')\" >> $_F\n  echo \"Label: migasfree $_NAME repository\" >> $_F\n  echo \"Origin: migasfree\" >> $_F\n  echo \"Suite: $_NAME\" >> $_F\n\n  calculate_hash \"MD5Sum:\" \"md5sum\" >> $_F\n  calculate_hash \"SHA1:\" \"sha1sum\" >> $_F\n  calculate_hash \"SHA256:\" \"sha256sum\" >> $_F\n  calculate_hash \"SHA512:\" \"sha512sum\" >> $_F\n\n  mv $_F Release\n\n  gpg -u migasfree-repository --homedir %KEYS%/.gnupg --clearsign -o InRelease Release\n  gpg -u migasfree-repository --homedir %KEYS%/.gnupg -abs -o Release.gpg Release\n}\n\ncd dists/$_NAME\ncreate_deploy\n",
                ]
            )]
        ),
    ]
