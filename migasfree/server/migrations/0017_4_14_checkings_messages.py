# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0016_4_14_repositories'),
    ]

    operations = [
        migrations.RenameField(
            model_name='Checking',
            old_name='active',
            new_name='enabled',
        ),
        migrations.AlterField(
            model_name='Checking',
            name='enabled',
            field=models.BooleanField(
                default=True,
                verbose_name='enabled'
            ),
        ),
        migrations.RenameField(
            model_name='Message',
            old_name='date',
            new_name='updated_at',
        ),
        migrations.AlterField(
            model_name='Message',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                default=django.utils.timezone.now,
                verbose_name='date'
            ),
            preserve_default=False,
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_checking SET code=%s WHERE id=5;",
                [
                    "from django.conf import settings\nfrom datetime import datetime, timedelta\nfrom migasfree.server.models import Message\nurl = '/computer_messages/'\nmsg = 'Computer updating now'\nt = datetime.now() - timedelta(0, settings.MIGASFREE_SECONDS_MESSAGE_ALERT)\nresult = Message.objects.filter(updated_at__gt=t).count()\nalert = 'info'\ntarget = 'computer'\n"
                ]
            )],
            [(
                "UPDATE server_checking SET code=%s WHERE id=5;",
                [
                    "from django.conf import settings\nfrom datetime import datetime, timedelta\nfrom migasfree.server.models import Message\nurl = '/computer_messages/'\nmsg = 'Computer updating now'\nt = datetime.now() - timedelta(0, settings.MIGASFREE_SECONDS_MESSAGE_ALERT)\nresult = Message.objects.filter(date__gt=t).count()\nalert = 'info'\ntarget = 'computer'\n"
                ]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_checking SET code=%s WHERE id=6;",
                [
                    "from django.conf import settings\nfrom datetime import datetime, timedelta\nfrom migasfree.server.models import Message\nurl = '/computer_messages/'\nmsg = 'Computer delayed' \nt = datetime.now() - timedelta(0, settings.MIGASFREE_SECONDS_MESSAGE_ALERT)\nresult = Message.objects.filter(updated_at__lt=t).count()\nalert = 'warning'\ntarget = 'computer'\n"
                ]
            )],
            [(
                "UPDATE server_checking SET code=%s WHERE id=6;",
                [
                    "from django.conf import settings\nfrom datetime import datetime, timedelta\nfrom migasfree.server.models import Message\nurl = '/computer_messages/'\nmsg = 'Computer delayed' \nt = datetime.now() - timedelta(0, settings.MIGASFREE_SECONDS_MESSAGE_ALERT)\nresult = Message.objects.filter(date__lt=t).count()\nalert = 'warning'\ntarget = 'computer'\n"
                ]
            )]
        ),
        migrations.DeleteModel(
            name='MessageServer',
        ),
        migrations.RunSQL(
            "DELETE FROM server_checking WHERE id=7;",
            migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            "DELETE FROM server_checking WHERE id=8;",
            migrations.RunSQL.noop
        ),
    ]
