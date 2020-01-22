# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0038_4_18_domain_admins'),
    ]

    operations = [
        migrations.RunSQL(
            [(
                "UPDATE server_property SET code=%s WHERE id=9 AND code LIKE '/proc/bus/pci';",
                [
                    "from __future__ import print_function\nimport sys\nimport subprocess\nimport platform\n\n\n_platform = platform.system()\nif _platform == 'Linux':\n    cmd_linux = \"\"\"r=''\n      if [ `lspci -n | sed -n 1p | awk '{print $2}'` = 'Class' ]\n      then\n        dev=`lspci -n | awk '{print $4}'`\n      else\n        dev=`lspci -n | awk '{print $3}'`\n      fi\n      for l in $dev\n      do\n        n=`lspci -d $l | awk '{for (i = 2; i <= NF; ++i) print $i}' | tr \"\\n\" \" \" | sed 's/,//g'`\n        r=\"$r$l~$n,\"\n      done\n      echo $r\"\"\"\n    out, err = subprocess.Popen(cmd_linux, stdout=subprocess.PIPE, shell=True).communicate()\n    if sys.version_info.major <= 2:\n        print(out,)\n    else:\n        print(out.decode(),)\nelif _platform == 'Windows':\n    print(\"none\",)\nelse:\n    print(\"none\",)",
                ]
            )],
            [(
                "UPDATE server_property SET code=%s WHERE id=9 AND code LIKE '/proc/bus/pci';",
                [
                    "import subprocess\nimport platform\nimport os\n\n_platform = platform.system()\nif _platform == 'Linux':\n    if os.path.exists('/proc/bus/pci'):\n        cmd_linux=\"\"\"r=''\n      if [ \"$(lspci -n | sed -n 1p | awk '{print $2}')\" = 'Class' ]; then\n        dev=$(lspci -n |awk '{print $4}')\n      else\n        dev=$(lspci -n | awk '{print $3}')\n      fi\n      for l in $dev\n      do\n        n=$(lspci -d $l | awk '{for (i = 2; i <=NF;++i) print $i}' | tr \"\\n\" \" \" | sed 's/,//g')\n        r=\"$r$l~$n,\"\n      done\n      echo $r\"\"\"\n        (out, err) = subprocess.Popen(cmd_linux, stdout=subprocess.PIPE, shell=True).communicate()\n        if out.strip():\n            print out.strip(),\n        else:\n                print 'none',\n    else:\n        print 'none',\nelif _platform == 'Windows':\n    print 'none',\n\nelse:\n    print 'none',",
                ]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_property SET code=%s WHERE id=8 AND code LIKE 'migasfree_client.network';",
                [
                    "import migasfree_client.network\nprint(migasfree_client.network.get_network_info()['net'])",
                ]
            )],
            [(
                "UPDATE server_property SET code=%s WHERE id=8 AND code LIKE 'migasfree_client.network';",
                [
                    "import migasfree_client.network\nprint migasfree_client.network.get_network_info()['net']",
                ]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_property SET code=%s WHERE id=7 AND code LIKE 'import platform';",
                [
                    "import platform\nprint(platform.node())",
                ]
            )],
            [(
                "UPDATE server_property SET code=%s WHERE id=7 AND code LIKE 'import platform';",
                [
                    "import platform\nprint platform.node()",
                ]
            )]
        ),
    ]
