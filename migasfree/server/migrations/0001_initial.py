# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import migasfree.server.models.common
import django.contrib.auth.models
import django.db.models.deletion
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=250, verbose_name='value')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
            ],
            options={
                'verbose_name': 'Attribute',
                'verbose_name_plural': 'Attributes',
                'permissions': (('can_save_attribute', 'Can save Attribute'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='AttributeSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('attributes', models.ManyToManyField(
                    help_text='Assigned Attributes',
                    to='server.Attribute',
                    null=True, verbose_name='attributes', blank=True
                )),
                ('excludes', models.ManyToManyField(
                    related_name='ExcludeAttributeGroup',
                    to='server.Attribute', blank=True,
                    help_text='Excluded Attributes', null=True, verbose_name='excludes'
                )),
            ],
            options={
                'verbose_name': 'Attributes Set',
                'verbose_name_plural': 'Attributes Sets',
                'permissions': (('can_save_attributteset', 'Can save Attributes Set'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='AutoCheckError',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField(
                    help_text='Pattern to search . See https://docs.python.org/2/library/re.html#module-re',
                    null=True, verbose_name='message', blank=True
                )),
            ],
            options={
                'verbose_name': 'Auto Check Error',
                'verbose_name_plural': 'Auto Check Errors',
                'permissions': (('can_save_autocheckerror', 'Can save Auto Check Error'),),
            },
        ),
        migrations.CreateModel(
            name='Checking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, unique=True, null=True, verbose_name='name', blank=True)),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('code', models.TextField(
                    help_text="Code django. <br><b>VARIABLES TO SETTINGS:</b><br><b>result</b>: a number. If result<>0 the checking is show in the section Status. Default is 0<br><b>alert</b>: type of alert. Default is 'info'. Enumeration value: {'info' | 'warning' | 'danger'}<br><b>url</b>: link. Default is '/'<br><b>msg</b>: The text to show. Default is the field name.<br><b>target</b>: Enumeration value: {'computer' | 'server'}",
                    verbose_name='code', blank=True
                )),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('alert', models.BooleanField(default=True, verbose_name='alert')),
            ],
            options={
                'verbose_name': 'Checking',
                'verbose_name_plural': 'Checkings',
                'permissions': (('can_save_checking', 'Can save Checking'),),
            },
        ),
        migrations.CreateModel(
            name='Computer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, null=True, verbose_name='name', blank=True)),
                ('uuid', models.CharField(
                    null=True, default=b'', max_length=36,
                    blank=True, unique=True, verbose_name='uuid'
                )),
                ('dateinput', models.DateField(
                    help_text='Date of input of Computer in migasfree system',
                    verbose_name='date input'
                )),
                ('ip', models.CharField(max_length=50, null=True, verbose_name='ip', blank=True)),
                ('software', models.TextField(
                    help_text='gap between software base packages and computer ones',
                    null=True, verbose_name='software inventory', blank=True
                )),
                ('history_sw', models.TextField(default=b'', null=True, verbose_name='software history', blank=True)),
                ('devices_copy', models.TextField(verbose_name='devices copy', null=True, editable=False)),
                ('datelastupdate', models.DateTimeField(null=True, verbose_name='last update')),
                ('datehardware', models.DateTimeField(null=True, verbose_name='last hardware capture', blank=True)),
            ],
            options={
                'verbose_name': 'Computer',
                'verbose_name_plural': 'Computers',
                'permissions': (('can_save_computer', 'Can save Computer'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, unique=True, null=True, verbose_name='name', blank=True)),
                ('data', models.TextField(default=b'{}', null=True, verbose_name='data')),
            ],
            options={
                'verbose_name': 'Device',
                'verbose_name_plural': 'Devices',
                'permissions': (('can_save_device', 'Can save Device'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='DeviceConnection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, null=True, verbose_name='name', blank=True)),
                ('fields', models.CharField(
                    help_text='Fields separated by comma', max_length=100,
                    null=True, verbose_name='fields', blank=True
                )),
            ],
            options={
                'verbose_name': 'Device (Connection)',
                'verbose_name_plural': 'Device (Connections)',
                'permissions': (('can_save_deviceconnection', 'Can save Device Connection'),),
            },
        ),
        migrations.CreateModel(
            name='DeviceDriver',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('install', models.TextField(null=True, verbose_name='packages to install', blank=True)),
            ],
            options={
                'verbose_name': 'Device (Driver)',
                'verbose_name_plural': 'Device (Driver)',
                'permissions': (('can_save_devicedriver', 'Can save Device Driver'),),
            },
        ),
        migrations.CreateModel(
            name='DeviceFeature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, unique=True, null=True, verbose_name='name', blank=True)),
            ],
            options={
                'verbose_name': 'Device (Feature)',
                'verbose_name_plural': 'Device (Feature)',
                'permissions': (('can_save_devicefeature', 'Can save Device Feature'),),
            },
        ),
        migrations.CreateModel(
            name='DeviceLogical',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device', models.ForeignKey(verbose_name='device', to='server.Device')),
                ('feature', models.ForeignKey(verbose_name='feature', to='server.DeviceFeature')),
            ],
            options={
                'verbose_name': 'Device (Logical)',
                'verbose_name_plural': 'Device (Logical)',
                'permissions': (('can_save_devicelogical', 'Can save Device Logical'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='DeviceManufacturer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, unique=True, null=True, verbose_name='name', blank=True)),
            ],
            options={
                'verbose_name': 'Device (Manufacturer)',
                'verbose_name_plural': 'Device (Manufacturers)',
                'permissions': (('can_save_devicemanufacturer', 'Can save Device Manufacturer'),),
            },
        ),
        migrations.CreateModel(
            name='DeviceModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, null=True, verbose_name='name', blank=True)),
                ('connections', models.ManyToManyField(
                    to='server.DeviceConnection', null=True,
                    verbose_name='connections', blank=True
                )),
            ],
            options={
                'verbose_name': 'Device (Model)',
                'verbose_name_plural': 'Device (Models)',
                'permissions': (('can_save_devicemodel', 'Can save Device Model'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='DeviceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, unique=True, null=True, verbose_name='name', blank=True)),
            ],
            options={
                'verbose_name': 'Device (Type)',
                'verbose_name_plural': 'Device (Types)',
                'permissions': (('can_save_devicetype', 'Can save Device Type'),),
            },
        ),
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('error', models.TextField(null=True, verbose_name='error', blank=True)),
                ('checked', models.BooleanField(default=False, verbose_name='checked')),
                ('computer', models.ForeignKey(verbose_name='computer', to='server.Computer')),
            ],
            options={
                'verbose_name': 'Error',
                'verbose_name_plural': 'Errors',
                'permissions': (('can_save_error', 'Can save Error'),),
            },
        ),
        migrations.CreateModel(
            name='Fault',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('text', models.TextField(null=True, verbose_name='text', blank=True)),
                ('checked', models.BooleanField(default=False, verbose_name='checked')),
                ('computer', models.ForeignKey(verbose_name='computer', to='server.Computer')),
            ],
            options={
                'verbose_name': 'Fault',
                'verbose_name_plural': 'Faults',
                'permissions': (('can_save_fault', 'Can save Fault'),),
            },
        ),
        migrations.CreateModel(
            name='FaultDef',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='name')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('language', models.IntegerField(
                    default=0,
                    verbose_name='programming language',
                    choices=[(0, b'bash'), (1, b'python'), (2, b'perl'), (3, b'php'), (4, b'ruby'), (5, b'cmd')]
                )),
                ('code', models.TextField(verbose_name='Code', blank=True)),
                ('attributes', models.ManyToManyField(
                    to='server.Attribute', null=True,
                    verbose_name='attributes', blank=True
                )),
            ],
            options={
                'verbose_name': 'Fault Definition',
                'verbose_name_plural': 'Faults Definition',
                'permissions': (('can_save_faultdef', 'Can save Fault Definition'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='HwCapability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(verbose_name='name', blank=True)),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
            ],
            options={
                'verbose_name': 'Hardware Capability',
                'verbose_name_plural': 'Hardware Capabilities',
            },
        ),
        migrations.CreateModel(
            name='HwConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(verbose_name='name', blank=True)),
                ('value', models.TextField(null=True, verbose_name='value', blank=True)),
            ],
            options={
                'verbose_name': 'Hardware Capability',
                'verbose_name_plural': 'Hardware Capabilities',
            },
        ),
        migrations.CreateModel(
            name='HwLogicalName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(verbose_name='name', blank=True)),
            ],
            options={
                'verbose_name': 'Hardware Logical Name',
                'verbose_name_plural': 'Hardware Logical Names',
            },
        ),
        migrations.CreateModel(
            name='HwNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.IntegerField(verbose_name='width')),
                ('width', models.IntegerField(null=True, verbose_name='width')),
                ('name', models.TextField(verbose_name='id', blank=True)),
                ('classname', models.TextField(verbose_name='class', blank=True)),
                ('enabled', models.BooleanField(default=False, verbose_name='enabled')),
                ('claimed', models.BooleanField(default=False, verbose_name='claimed')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('vendor', models.TextField(null=True, verbose_name='vendor', blank=True)),
                ('product', models.TextField(null=True, verbose_name='product', blank=True)),
                ('version', models.TextField(null=True, verbose_name='version', blank=True)),
                ('serial', models.TextField(null=True, verbose_name='serial', blank=True)),
                ('businfo', models.TextField(null=True, verbose_name='businfo', blank=True)),
                ('physid', models.TextField(null=True, verbose_name='physid', blank=True)),
                ('slot', models.TextField(null=True, verbose_name='slot', blank=True)),
                ('size', models.BigIntegerField(null=True, verbose_name='size')),
                ('capacity', models.BigIntegerField(null=True, verbose_name='capacity')),
                ('clock', models.IntegerField(null=True, verbose_name='clock')),
                ('dev', models.TextField(null=True, verbose_name='dev', blank=True)),
                ('icon', models.TextField(null=True, verbose_name='icon', blank=True)),
                ('computer', models.ForeignKey(verbose_name='computer', to='server.Computer')),
                ('parent', models.ForeignKey(
                    related_name='child', verbose_name='parent',
                    blank=True, to='server.HwNode', null=True
                )),
            ],
            options={
                'verbose_name': 'Hardware Node',
                'verbose_name_plural': 'Hardware Nodes',
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='Login',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=0, verbose_name='date')),
                ('attributes', models.ManyToManyField(
                    help_text='Sent attributes', to='server.Attribute',
                    null=True, verbose_name='attributes', blank=True
                )),
                ('computer', models.ForeignKey(verbose_name='computer', to='server.Computer')),
            ],
            options={
                'verbose_name': 'Login',
                'verbose_name_plural': 'Logins',
                'permissions': (('can_save_login', 'Can save Login'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(null=True, verbose_name='text', blank=True)),
                ('date', models.DateTimeField(default=0, verbose_name='date')),
                ('computer', models.ForeignKey(verbose_name='computer', to='server.Computer', unique=True)),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
                'permissions': (('can_save_message', 'Can save Message'),),
            },
        ),
        migrations.CreateModel(
            name='MessageServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(null=True, verbose_name='text', blank=True)),
                ('date', models.DateTimeField(default=0, verbose_name='date')),
            ],
            options={
                'verbose_name': 'Message Server',
                'verbose_name_plural': 'Messages Server',
                'permissions': (('can_save_messageserver', 'Can save Message Server'),),
            },
        ),
        migrations.CreateModel(
            name='Migration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('computer', models.ForeignKey(verbose_name='computer', to='server.Computer')),
            ],
            options={
                'verbose_name': 'Migration',
                'verbose_name_plural': 'Migrations',
                'permissions': (('can_save_migration', 'Can save Migration'),),
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('notification', models.TextField(null=True, verbose_name='notification', blank=True)),
                ('checked', models.BooleanField(default=False, verbose_name='checked')),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'permissions': (('can_save_notification', 'Can save Notification'),),
            },
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
            ],
            options={
                'verbose_name': 'Package/Set',
                'verbose_name_plural': 'Packages/Sets',
                'permissions': (('can_save_package', 'Can save Package'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, unique=True, null=True, verbose_name='name', blank=True)),
            ],
            options={
                'verbose_name': 'Platform',
                'verbose_name_plural': 'Platforms',
                'permissions': (('can_save_platform', 'Can save Platform'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='Pms',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='name')),
                ('slug', models.CharField(
                    default=b'REPOSITORIES',
                    max_length=50, null=True,
                    verbose_name='slug', blank=True
                )),
                ('createrepo', models.TextField(
                    help_text='Code bash. Define how create the metadata of repositories in the migasfree server.',
                    null=True, verbose_name='create repository', blank=True
                )),
                ('info', models.TextField(
                    help_text='Code bash. Define how get info of packages in the server',
                    null=True, verbose_name='package information', blank=True
                )),
            ],
            options={
                'verbose_name': 'Package Management System',
                'verbose_name_plural': 'Package Management Systems',
                'permissions': (('can_save_pms', 'Can save Package Management System'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prefix', models.CharField(unique=True, max_length=3, verbose_name='prefix')),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('language', models.IntegerField(
                    default=1,
                    verbose_name='programming language',
                    choices=[(0, b'bash'), (1, b'python'), (2, b'perl'), (3, b'php'), (4, b'ruby'), (5, b'cmd')]
                )),
                ('code', models.TextField(
                    help_text="This code will execute in the client computer, and it must put in the standard output the value of the attribute correspondent to this property.<br>The format of this value is 'name~description', where 'description' is optional.<br><b>Example of code:</b><br>#Create a attribute with the name of computer from bash<br> echo $HOSTNAME",
                    verbose_name='Code', blank=True
                )),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('kind', models.CharField(
                    default=b'N',
                    max_length=1,
                    verbose_name='kind',
                    choices=[(b'N', 'NORMAL'), (b'-', 'LIST'), (b'L', 'ADDS LEFT'), (b'R', 'ADDS RIGHT')]
                )),
                ('auto', models.BooleanField(
                    default=True,
                    help_text='automatically add the attribute to database',
                    verbose_name='auto'
                )),
                ('tag', models.BooleanField(default=False, help_text='tag', verbose_name='tag')),
            ],
            options={
                'verbose_name': 'Property',
                'verbose_name_plural': 'Properties',
                'permissions': (('can_save_property', 'Can save Property'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, unique=True, null=True, verbose_name='name', blank=True)),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('code', models.TextField(
                    default=b"query=Package.objects.filter(version=VERSION).filter(Q(repository__id__exact=None))\nfields=('id','name','store__name')\ntitles=('id','name','store')",
                    help_text='Code Django: version=user.version, query=QuerySet, fields=list of QuerySet fields names to show, titles=list of QuerySet fields titles',
                    null=True, verbose_name='code', blank=True
                )),
                ('parameters', models.TextField(
                    help_text=b'Code Django: ',
                    null=True,
                    verbose_name='parameters', blank=True
                )),
            ],
            options={
                'verbose_name': 'Query',
                'verbose_name_plural': 'Queries',
                'permissions': (('can_save_query', 'Can save Query'),),
            },
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('active', models.BooleanField(
                    default=True,
                    help_text='if you uncheck this field, the repository is hidden for all computers.',
                    verbose_name='active'
                )),
                ('date', models.DateField(help_text='Date initial for distribute.', verbose_name='date')),
                ('comment', models.TextField(null=True, verbose_name='comment', blank=True)),
                ('toinstall', models.TextField(null=True, verbose_name='packages to install', blank=True)),
                ('toremove', models.TextField(null=True, verbose_name='packages to remove', blank=True)),
                ('defaultpreinclude', models.TextField(
                    null=True,
                    verbose_name='default preinclude packages',
                    blank=True
                )),
                ('defaultinclude', models.TextField(
                    null=True,
                    verbose_name='default include packages',
                    blank=True
                )),
                ('defaultexclude', models.TextField(
                    null=True,
                    verbose_name='default exclude packages',
                    blank=True
                )),
                ('attributes', models.ManyToManyField(
                    help_text='Assigned Attributes',
                    to='server.Attribute',
                    null=True, verbose_name='attributes', blank=True
                )),
                ('excludes', models.ManyToManyField(
                    related_name='ExcludeAttribute',
                    to='server.Attribute',
                    blank=True, help_text='Excluded Attributes',
                    null=True, verbose_name='excludes'
                )),
                ('packages', models.ManyToManyField(
                    help_text='Assigned Packages',
                    to='server.Package',
                    null=True, verbose_name='Packages/Set', blank=True
                )),
            ],
            options={
                'verbose_name': 'Repository',
                'verbose_name_plural': 'Repositories',
                'permissions': (('can_save_repository', 'Can save Repository'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'default', unique=True, max_length=50, verbose_name='name')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
            ],
            options={
                'verbose_name': 'Schedule',
                'verbose_name_plural': 'Schedules',
                'permissions': (('can_save_schedule', 'Can save Schedule'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='ScheduleDelay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('delay', models.IntegerField(verbose_name='delay')),
                ('duration', models.IntegerField(
                    default=1, verbose_name='duration',
                    validators=[django.core.validators.MinValueValidator(1)]
                )),
                ('attributes', models.ManyToManyField(
                    to='server.Attribute', null=True,
                    verbose_name='attributes', blank=True
                )),
                ('schedule', models.ForeignKey(verbose_name='schedule', to='server.Schedule')),
            ],
            options={
                'verbose_name': 'Schedule Delay',
                'verbose_name_plural': 'Schedule Delays',
                'permissions': (('can_save_scheduledelay', 'Can save Schedule Delay'),),
            },
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='name')),
            ],
            options={
                'verbose_name': 'Store',
                'verbose_name_plural': 'Stores',
                'permissions': (('can_save_store', 'Can save Store'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='Update',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('computer', models.ForeignKey(verbose_name='computer', to='server.Computer')),
            ],
            options={
                'verbose_name': 'Update',
                'verbose_name_plural': 'Updates',
                'permissions': (('can_save_update', 'Can save Update'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='name')),
                ('fullname', models.CharField(max_length=100, verbose_name='fullname')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'permissions': (('can_save_user', 'Can save User'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user_ptr', models.OneToOneField(
                    parent_link=True, auto_created=True, primary_key=True,
                    serialize=False, to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'User Profile',
                'verbose_name_plural': 'User Profiles',
                'permissions': (('can_save_userprofile', 'Can save User Profile'),),
            },
            bases=('auth.user', migasfree.server.models.common.MigasLink),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='name')),
                ('computerbase', models.CharField(
                    default=b'---',
                    help_text='Computer with the actual line software',
                    max_length=50, verbose_name='Actual line computer'
                )),
                ('base', models.TextField(
                    help_text='List ordered of packages of actual line computer',
                    verbose_name='Actual line packages', blank=True
                )),
                ('autoregister', models.BooleanField(
                    default=False,
                    help_text='Is not neccesary a user for register the computer in database and get the keys.',
                    verbose_name='autoregister'
                )),
                ('platform', models.ForeignKey(verbose_name='platform', to='server.Platform')),
                ('pms', models.ForeignKey(verbose_name='package management system', to='server.Pms')),
            ],
            options={
                'verbose_name': 'Version',
                'verbose_name_plural': 'Versions',
                'permissions': (('can_save_version', 'Can save Version'),),
            },
            bases=(models.Model, migasfree.server.models.common.MigasLink),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='version',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name='version',
                to='server.Version',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='update',
            name='user',
            field=models.ForeignKey(verbose_name='user', to='server.User'),
        ),
        migrations.AddField(
            model_name='update',
            name='version',
            field=models.ForeignKey(verbose_name='version', to='server.Version', null=True),
        ),
        migrations.AddField(
            model_name='store',
            name='version',
            field=models.ForeignKey(verbose_name='version', to='server.Version'),
        ),
        migrations.AddField(
            model_name='repository',
            name='schedule',
            field=models.ForeignKey(verbose_name='schedule', blank=True, to='server.Schedule', null=True),
        ),
        migrations.AddField(
            model_name='repository',
            name='version',
            field=models.ForeignKey(verbose_name='version', to='server.Version'),
        ),
        migrations.AddField(
            model_name='package',
            name='store',
            field=models.ForeignKey(verbose_name='store', to='server.Store'),
        ),
        migrations.AddField(
            model_name='package',
            name='version',
            field=models.ForeignKey(verbose_name='version', to='server.Version'),
        ),
        migrations.AddField(
            model_name='migration',
            name='version',
            field=models.ForeignKey(verbose_name='version', to='server.Version'),
        ),
        migrations.AddField(
            model_name='login',
            name='user',
            field=models.ForeignKey(verbose_name='user', to='server.User'),
        ),
        migrations.AddField(
            model_name='hwlogicalname',
            name='node',
            field=models.ForeignKey(verbose_name='hardware node', to='server.HwNode'),
        ),
        migrations.AddField(
            model_name='hwconfiguration',
            name='node',
            field=models.ForeignKey(verbose_name='hardware node', to='server.HwNode'),
        ),
        migrations.AddField(
            model_name='hwcapability',
            name='node',
            field=models.ForeignKey(verbose_name='hardware node', to='server.HwNode'),
        ),
        migrations.AddField(
            model_name='faultdef',
            name='users',
            field=models.ManyToManyField(to='server.UserProfile', null=True, verbose_name='users', blank=True),
        ),
        migrations.AddField(
            model_name='fault',
            name='faultdef',
            field=models.ForeignKey(verbose_name='fault definition', to='server.FaultDef'),
        ),
        migrations.AddField(
            model_name='fault',
            name='version',
            field=models.ForeignKey(verbose_name='version', to='server.Version'),
        ),
        migrations.AddField(
            model_name='error',
            name='version',
            field=models.ForeignKey(verbose_name='version', to='server.Version'),
        ),
        migrations.AddField(
            model_name='devicemodel',
            name='devicetype',
            field=models.ForeignKey(verbose_name='type', to='server.DeviceType'),
        ),
        migrations.AddField(
            model_name='devicemodel',
            name='manufacturer',
            field=models.ForeignKey(verbose_name='manufacturer', to='server.DeviceManufacturer'),
        ),
        migrations.AddField(
            model_name='devicedriver',
            name='feature',
            field=models.ForeignKey(verbose_name='feature', to='server.DeviceFeature'),
        ),
        migrations.AddField(
            model_name='devicedriver',
            name='model',
            field=models.ForeignKey(verbose_name='model', to='server.DeviceModel'),
        ),
        migrations.AddField(
            model_name='devicedriver',
            name='version',
            field=models.ForeignKey(verbose_name='version', to='server.Version'),
        ),
        migrations.AddField(
            model_name='deviceconnection',
            name='devicetype',
            field=models.ForeignKey(verbose_name='device type', to='server.DeviceType'),
        ),
        migrations.AddField(
            model_name='device',
            name='connection',
            field=models.ForeignKey(verbose_name='connection', to='server.DeviceConnection'),
        ),
        migrations.AddField(
            model_name='device',
            name='model',
            field=models.ForeignKey(verbose_name='model', to='server.DeviceModel'),
        ),
        migrations.AddField(
            model_name='computer',
            name='devices_logical',
            field=models.ManyToManyField(to='server.DeviceLogical', null=True, verbose_name='devices', blank=True),
        ),
        migrations.AddField(
            model_name='computer',
            name='tags',
            field=models.ManyToManyField(to='server.Attribute', null=True, verbose_name='tags', blank=True),
        ),
        migrations.AddField(
            model_name='computer',
            name='version',
            field=models.ForeignKey(verbose_name='version', to='server.Version'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='property_att',
            field=models.ForeignKey(verbose_name='Property', to='server.Property'),
        ),
        migrations.CreateModel(
            name='Att',
            fields=[
            ],
            options={
                'verbose_name': 'Attribute/Tag',
                'proxy': True,
                'verbose_name_plural': 'Attributes/Tags',
            },
            bases=('server.attribute',),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
            ],
            options={
                'verbose_name': 'Tag',
                'proxy': True,
                'verbose_name_plural': 'Tags',
            },
            bases=('server.attribute',),
        ),
        migrations.CreateModel(
            name='TagType',
            fields=[
            ],
            options={
                'verbose_name': 'Tag Type',
                'proxy': True,
                'verbose_name_plural': 'Tag Types',
            },
            bases=('server.property',),
        ),
        migrations.AlterUniqueTogether(
            name='store',
            unique_together={('name', 'version')},
        ),
        migrations.AlterUniqueTogether(
            name='scheduledelay',
            unique_together={('schedule', 'delay')},
        ),
        migrations.AlterUniqueTogether(
            name='repository',
            unique_together={('name', 'version')},
        ),
        migrations.AlterUniqueTogether(
            name='package',
            unique_together={('name', 'version')},
        ),
        migrations.AlterUniqueTogether(
            name='login',
            unique_together={('computer',)},
        ),
        migrations.AlterUniqueTogether(
            name='hwconfiguration',
            unique_together={('name', 'node')},
        ),
        migrations.AlterUniqueTogether(
            name='hwcapability',
            unique_together={('name', 'node')},
        ),
        migrations.AlterUniqueTogether(
            name='devicemodel',
            unique_together={('devicetype', 'manufacturer', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='devicelogical',
            unique_together={('device', 'feature')},
        ),
        migrations.AlterUniqueTogether(
            name='devicedriver',
            unique_together={('model', 'version', 'feature')},
        ),
        migrations.AlterUniqueTogether(
            name='deviceconnection',
            unique_together={('devicetype', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='device',
            unique_together={('connection', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='attribute',
            unique_together={('property_att', 'value')},
        ),
    ]
