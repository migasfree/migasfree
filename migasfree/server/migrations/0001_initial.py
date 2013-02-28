# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table('server_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('fullname', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('server', ['User'])

        # Adding model 'Query'
        db.create_table('server_query', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.TextField')(default="query=Package.objects.filter(version=VERSION).filter(Q(repository__id__exact=None))\nfields=('id','name','store__name')\ntitles=('id','name','store')", null=True, blank=True)),
            ('parameters', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('server', ['Query'])

        # Adding model 'Checking'
        db.create_table('server_checking', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('server', ['Checking'])

        # Adding model 'AutoCheckError'
        db.create_table('server_autocheckerror', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('server', ['AutoCheckError'])

        # Adding model 'Pms'
        db.create_table('server_pms', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('slug', self.gf('django.db.models.fields.CharField')(default='REPOSITORIES', max_length=50, null=True, blank=True)),
            ('createrepo', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('repository', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('server', ['Pms'])

        # Adding model 'Property'
        db.create_table('server_property', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('prefix', self.gf('django.db.models.fields.CharField')(unique=True, max_length=3)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('language', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('code', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('before_insert', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('after_insert', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(default='N', max_length=1)),
            ('auto', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('server', ['Property'])

        # Adding model 'Version'
        db.create_table('server_version', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('pms', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Pms'])),
            ('computerbase', self.gf('django.db.models.fields.CharField')(default='---', max_length=50)),
            ('base', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('autoregister', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('platform', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('server', ['Version'])

        # Adding model 'Attribute'
        db.create_table('server_attribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('property_att', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Property'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('server', ['Attribute'])

        # Adding unique constraint on 'Attribute', fields ['property_att', 'value']
        db.create_unique('server_attribute', ['property_att_id', 'value'])

        # Adding model 'DeviceType'
        db.create_table('server_devicetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('server', ['DeviceType'])

        # Adding model 'DeviceManufacturer'
        db.create_table('server_devicemanufacturer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('server', ['DeviceManufacturer'])

        # Adding model 'DeviceConnection'
        db.create_table('server_deviceconnection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('fields', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('install', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('remove', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('devicetype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.DeviceType'])),
        ))
        db.send_create_signal('server', ['DeviceConnection'])

        # Adding unique constraint on 'DeviceConnection', fields ['devicetype', 'name']
        db.create_unique('server_deviceconnection', ['devicetype_id', 'name'])

        # Adding model 'DeviceFile'
        db.create_table('server_devicefile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('server', ['DeviceFile'])

        # Adding model 'DeviceModel'
        db.create_table('server_devicemodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('manufacturer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.DeviceManufacturer'])),
            ('devicetype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.DeviceType'])),
            ('devicefile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.DeviceFile'], null=True, blank=True)),
            ('preinstall', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('postinstall', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('preremove', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('postremove', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('server', ['DeviceModel'])

        # Adding unique constraint on 'DeviceModel', fields ['devicetype', 'manufacturer', 'name']
        db.create_unique('server_devicemodel', ['devicetype_id', 'manufacturer_id', 'name'])

        # Adding M2M table for field connections on 'DeviceModel'
        db.create_table('server_devicemodel_connections', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('devicemodel', models.ForeignKey(orm['server.devicemodel'], null=False)),
            ('deviceconnection', models.ForeignKey(orm['server.deviceconnection'], null=False))
        ))
        db.create_unique('server_devicemodel_connections', ['devicemodel_id', 'deviceconnection_id'])

        # Adding model 'Device'
        db.create_table('server_device', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True, null=True, blank=True)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.DeviceModel'])),
            ('connection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.DeviceConnection'])),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True, null=True, blank=True)),
            ('information', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('server', ['Device'])

        # Adding unique constraint on 'Device', fields ['connection', 'name']
        db.create_unique('server_device', ['connection_id', 'name'])

        # Adding model 'Computer'
        db.create_table('server_computer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Version'])),
            ('dateinput', self.gf('django.db.models.fields.DateField')()),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('software', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('history_sw', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('devices_copy', self.gf('django.db.models.fields.TextField')(null=True)),
            ('devices_modified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('datelastupdate', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('server', ['Computer'])

        # Adding M2M table for field devices on 'Computer'
        db.create_table('server_computer_devices', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('computer', models.ForeignKey(orm['server.computer'], null=False)),
            ('device', models.ForeignKey(orm['server.device'], null=False))
        ))
        db.create_unique('server_computer_devices', ['computer_id', 'device_id'])

        # Adding model 'Message'
        db.create_table('server_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('computer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Computer'], unique=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
        ))
        db.send_create_signal('server', ['Message'])

        # Adding model 'Update'
        db.create_table('server_update', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('computer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Computer'])),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Version'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
        ))
        db.send_create_signal('server', ['Update'])

        # Adding model 'Error'
        db.create_table('server_error', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('computer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Computer'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('error', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('checked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Version'])),
        ))
        db.send_create_signal('server', ['Error'])

        # Adding model 'Login'
        db.create_table('server_login', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('computer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Computer'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.User'])),
        ))
        db.send_create_signal('server', ['Login'])

        # Adding unique constraint on 'Login', fields ['computer', 'user']
        db.create_unique('server_login', ['computer_id', 'user_id'])

        # Adding M2M table for field attributes on 'Login'
        db.create_table('server_login_attributes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('login', models.ForeignKey(orm['server.login'], null=False)),
            ('attribute', models.ForeignKey(orm['server.attribute'], null=False))
        ))
        db.create_unique('server_login_attributes', ['login_id', 'attribute_id'])

        # Adding model 'FaultDef'
        db.create_table('server_faultdef', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('language', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('code', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('server', ['FaultDef'])

        # Adding M2M table for field attributes on 'FaultDef'
        db.create_table('server_faultdef_attributes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('faultdef', models.ForeignKey(orm['server.faultdef'], null=False)),
            ('attribute', models.ForeignKey(orm['server.attribute'], null=False))
        ))
        db.create_unique('server_faultdef_attributes', ['faultdef_id', 'attribute_id'])

        # Adding model 'Fault'
        db.create_table('server_fault', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('computer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Computer'])),
            ('faultdef', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.FaultDef'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('checked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Version'])),
        ))
        db.send_create_signal('server', ['Fault'])

        # Adding model 'HwNode'
        db.create_table('server_hwnode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='child', null=True, to=orm['server.HwNode'])),
            ('level', self.gf('django.db.models.fields.IntegerField')()),
            ('width', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('computer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Computer'])),
            ('name', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('classname', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('claimed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('vendor', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('product', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('serial', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('businfo', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('physid', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('slot', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('size', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('capacity', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('clock', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('dev', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('icon', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('server', ['HwNode'])

        # Adding model 'HwCapability'
        db.create_table('server_hwcapability', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.HwNode'])),
            ('name', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('server', ['HwCapability'])

        # Adding unique constraint on 'HwCapability', fields ['name', 'node']
        db.create_unique('server_hwcapability', ['name', 'node_id'])

        # Adding model 'HwConfiguration'
        db.create_table('server_hwconfiguration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.HwNode'])),
            ('name', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('server', ['HwConfiguration'])

        # Adding unique constraint on 'HwConfiguration', fields ['name', 'node']
        db.create_unique('server_hwconfiguration', ['name', 'node_id'])

        # Adding model 'HwLogicalName'
        db.create_table('server_hwlogicalname', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.HwNode'])),
            ('name', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('server', ['HwLogicalName'])

        # Adding model 'Schedule'
        db.create_table('server_schedule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('server', ['Schedule'])

        # Adding model 'ScheduleDelay'
        db.create_table('server_scheduledelay', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('delay', self.gf('django.db.models.fields.IntegerField')()),
            ('schedule', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Schedule'])),
        ))
        db.send_create_signal('server', ['ScheduleDelay'])

        # Adding unique constraint on 'ScheduleDelay', fields ['schedule', 'delay']
        db.create_unique('server_scheduledelay', ['schedule_id', 'delay'])

        # Adding M2M table for field attributes on 'ScheduleDelay'
        db.create_table('server_scheduledelay_attributes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('scheduledelay', models.ForeignKey(orm['server.scheduledelay'], null=False)),
            ('attribute', models.ForeignKey(orm['server.attribute'], null=False))
        ))
        db.create_unique('server_scheduledelay_attributes', ['scheduledelay_id', 'attribute_id'])

        # Adding model 'Store'
        db.create_table('server_store', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Version'])),
        ))
        db.send_create_signal('server', ['Store'])

        # Adding unique constraint on 'Store', fields ['name', 'version']
        db.create_unique('server_store', ['name', 'version_id'])

        # Adding model 'Package'
        db.create_table('server_package', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Version'])),
            ('store', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Store'])),
        ))
        db.send_create_signal('server', ['Package'])

        # Adding unique constraint on 'Package', fields ['name', 'version']
        db.create_unique('server_package', ['name', 'version_id'])

        # Adding model 'Repository'
        db.create_table('server_repository', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Version'])),
            ('schedule', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Schedule'], null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('toinstall', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('toremove', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('server', ['Repository'])

        # Adding unique constraint on 'Repository', fields ['name', 'version']
        db.create_unique('server_repository', ['name', 'version_id'])

        # Adding M2M table for field packages on 'Repository'
        db.create_table('server_repository_packages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('repository', models.ForeignKey(orm['server.repository'], null=False)),
            ('package', models.ForeignKey(orm['server.package'], null=False))
        ))
        db.create_unique('server_repository_packages', ['repository_id', 'package_id'])

        # Adding M2M table for field attributes on 'Repository'
        db.create_table('server_repository_attributes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('repository', models.ForeignKey(orm['server.repository'], null=False)),
            ('attribute', models.ForeignKey(orm['server.attribute'], null=False))
        ))
        db.create_unique('server_repository_attributes', ['repository_id', 'attribute_id'])

        # Adding M2M table for field createpackages on 'Repository'
        db.create_table('server_repository_createpackages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('repository', models.ForeignKey(orm['server.repository'], null=False)),
            ('package', models.ForeignKey(orm['server.package'], null=False))
        ))
        db.create_unique('server_repository_createpackages', ['repository_id', 'package_id'])

        # Adding M2M table for field excludes on 'Repository'
        db.create_table('server_repository_excludes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('repository', models.ForeignKey(orm['server.repository'], null=False)),
            ('attribute', models.ForeignKey(orm['server.attribute'], null=False))
        ))
        db.create_unique('server_repository_excludes', ['repository_id', 'attribute_id'])

        # Adding model 'UserProfile'
        db.create_table('server_userprofile', (
            ('user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Version'])),
        ))
        db.send_create_signal('server', ['UserProfile'])


    def backwards(self, orm):
        # Removing unique constraint on 'Repository', fields ['name', 'version']
        db.delete_unique('server_repository', ['name', 'version_id'])

        # Removing unique constraint on 'Package', fields ['name', 'version']
        db.delete_unique('server_package', ['name', 'version_id'])

        # Removing unique constraint on 'Store', fields ['name', 'version']
        db.delete_unique('server_store', ['name', 'version_id'])

        # Removing unique constraint on 'ScheduleDelay', fields ['schedule', 'delay']
        db.delete_unique('server_scheduledelay', ['schedule_id', 'delay'])

        # Removing unique constraint on 'HwConfiguration', fields ['name', 'node']
        db.delete_unique('server_hwconfiguration', ['name', 'node_id'])

        # Removing unique constraint on 'HwCapability', fields ['name', 'node']
        db.delete_unique('server_hwcapability', ['name', 'node_id'])

        # Removing unique constraint on 'Login', fields ['computer', 'user']
        db.delete_unique('server_login', ['computer_id', 'user_id'])

        # Removing unique constraint on 'Device', fields ['connection', 'name']
        db.delete_unique('server_device', ['connection_id', 'name'])

        # Removing unique constraint on 'DeviceModel', fields ['devicetype', 'manufacturer', 'name']
        db.delete_unique('server_devicemodel', ['devicetype_id', 'manufacturer_id', 'name'])

        # Removing unique constraint on 'DeviceConnection', fields ['devicetype', 'name']
        db.delete_unique('server_deviceconnection', ['devicetype_id', 'name'])

        # Removing unique constraint on 'Attribute', fields ['property_att', 'value']
        db.delete_unique('server_attribute', ['property_att_id', 'value'])

        # Deleting model 'User'
        db.delete_table('server_user')

        # Deleting model 'Query'
        db.delete_table('server_query')

        # Deleting model 'Checking'
        db.delete_table('server_checking')

        # Deleting model 'AutoCheckError'
        db.delete_table('server_autocheckerror')

        # Deleting model 'Pms'
        db.delete_table('server_pms')

        # Deleting model 'Property'
        db.delete_table('server_property')

        # Deleting model 'Version'
        db.delete_table('server_version')

        # Deleting model 'Attribute'
        db.delete_table('server_attribute')

        # Deleting model 'DeviceType'
        db.delete_table('server_devicetype')

        # Deleting model 'DeviceManufacturer'
        db.delete_table('server_devicemanufacturer')

        # Deleting model 'DeviceConnection'
        db.delete_table('server_deviceconnection')

        # Deleting model 'DeviceFile'
        db.delete_table('server_devicefile')

        # Deleting model 'DeviceModel'
        db.delete_table('server_devicemodel')

        # Removing M2M table for field connections on 'DeviceModel'
        db.delete_table('server_devicemodel_connections')

        # Deleting model 'Device'
        db.delete_table('server_device')

        # Deleting model 'Computer'
        db.delete_table('server_computer')

        # Removing M2M table for field devices on 'Computer'
        db.delete_table('server_computer_devices')

        # Deleting model 'Message'
        db.delete_table('server_message')

        # Deleting model 'Update'
        db.delete_table('server_update')

        # Deleting model 'Error'
        db.delete_table('server_error')

        # Deleting model 'Login'
        db.delete_table('server_login')

        # Removing M2M table for field attributes on 'Login'
        db.delete_table('server_login_attributes')

        # Deleting model 'FaultDef'
        db.delete_table('server_faultdef')

        # Removing M2M table for field attributes on 'FaultDef'
        db.delete_table('server_faultdef_attributes')

        # Deleting model 'Fault'
        db.delete_table('server_fault')

        # Deleting model 'HwNode'
        db.delete_table('server_hwnode')

        # Deleting model 'HwCapability'
        db.delete_table('server_hwcapability')

        # Deleting model 'HwConfiguration'
        db.delete_table('server_hwconfiguration')

        # Deleting model 'HwLogicalName'
        db.delete_table('server_hwlogicalname')

        # Deleting model 'Schedule'
        db.delete_table('server_schedule')

        # Deleting model 'ScheduleDelay'
        db.delete_table('server_scheduledelay')

        # Removing M2M table for field attributes on 'ScheduleDelay'
        db.delete_table('server_scheduledelay_attributes')

        # Deleting model 'Store'
        db.delete_table('server_store')

        # Deleting model 'Package'
        db.delete_table('server_package')

        # Deleting model 'Repository'
        db.delete_table('server_repository')

        # Removing M2M table for field packages on 'Repository'
        db.delete_table('server_repository_packages')

        # Removing M2M table for field attributes on 'Repository'
        db.delete_table('server_repository_attributes')

        # Removing M2M table for field createpackages on 'Repository'
        db.delete_table('server_repository_createpackages')

        # Removing M2M table for field excludes on 'Repository'
        db.delete_table('server_repository_excludes')

        # Deleting model 'UserProfile'
        db.delete_table('server_userprofile')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'server.attribute': {
            'Meta': {'unique_together': "(('property_att', 'value'),)", 'object_name': 'Attribute'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'property_att': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Property']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'server.autocheckerror': {
            'Meta': {'object_name': 'AutoCheckError'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'server.checking': {
            'Meta': {'object_name': 'Checking'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'server.computer': {
            'Meta': {'object_name': 'Computer'},
            'dateinput': ('django.db.models.fields.DateField', [], {}),
            'datelastupdate': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'devices': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['server.Device']", 'null': 'True', 'blank': 'True'}),
            'devices_copy': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'devices_modified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'history_sw': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'software': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Version']"})
        },
        'server.device': {
            'Meta': {'unique_together': "(('connection', 'name'),)", 'object_name': 'Device'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.DeviceConnection']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'information': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.DeviceModel']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'server.deviceconnection': {
            'Meta': {'unique_together': "(('devicetype', 'name'),)", 'object_name': 'DeviceConnection'},
            'devicetype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.DeviceType']"}),
            'fields': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'install': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'remove': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'server.devicefile': {
            'Meta': {'object_name': 'DeviceFile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'server.devicemanufacturer': {
            'Meta': {'object_name': 'DeviceManufacturer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'server.devicemodel': {
            'Meta': {'unique_together': "(('devicetype', 'manufacturer', 'name'),)", 'object_name': 'DeviceModel'},
            'connections': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['server.DeviceConnection']", 'null': 'True', 'blank': 'True'}),
            'devicefile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.DeviceFile']", 'null': 'True', 'blank': 'True'}),
            'devicetype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.DeviceType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.DeviceManufacturer']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'postinstall': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'postremove': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'preinstall': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'preremove': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'server.devicetype': {
            'Meta': {'object_name': 'DeviceType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'server.error': {
            'Meta': {'object_name': 'Error'},
            'checked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'computer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Computer']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'error': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Version']"})
        },
        'server.fault': {
            'Meta': {'object_name': 'Fault'},
            'checked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'computer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Computer']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'faultdef': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.FaultDef']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Version']"})
        },
        'server.faultdef': {
            'Meta': {'object_name': 'FaultDef'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'attributes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['server.Attribute']", 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'server.hwcapability': {
            'Meta': {'unique_together': "(('name', 'node'),)", 'object_name': 'HwCapability'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.HwNode']"})
        },
        'server.hwconfiguration': {
            'Meta': {'unique_together': "(('name', 'node'),)", 'object_name': 'HwConfiguration'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.HwNode']"}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'server.hwlogicalname': {
            'Meta': {'object_name': 'HwLogicalName'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.HwNode']"})
        },
        'server.hwnode': {
            'Meta': {'object_name': 'HwNode'},
            'businfo': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'capacity': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'claimed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'classname': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'clock': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'computer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Computer']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dev': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'icon': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child'", 'null': 'True', 'to': "orm['server.HwNode']"}),
            'physid': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'slot': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'vendor': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'server.login': {
            'Meta': {'unique_together': "(('computer', 'user'),)", 'object_name': 'Login'},
            'attributes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['server.Attribute']", 'null': 'True', 'blank': 'True'}),
            'computer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Computer']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.User']"})
        },
        'server.message': {
            'Meta': {'object_name': 'Message'},
            'computer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Computer']", 'unique': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'server.package': {
            'Meta': {'unique_together': "(('name', 'version'),)", 'object_name': 'Package'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Store']"}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Version']"})
        },
        'server.pms': {
            'Meta': {'object_name': 'Pms'},
            'createrepo': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'repository': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'default': "'REPOSITORIES'", 'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'server.property': {
            'Meta': {'object_name': 'Property'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'after_insert': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'auto': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'before_insert': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'language': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'prefix': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'})
        },
        'server.query': {
            'Meta': {'object_name': 'Query'},
            'code': ('django.db.models.fields.TextField', [], {'default': '"query=Package.objects.filter(version=VERSION).filter(Q(repository__id__exact=None))\\nfields=(\'id\',\'name\',\'store__name\')\\ntitles=(\'id\',\'name\',\'store\')"', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'parameters': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'server.repository': {
            'Meta': {'unique_together': "(('name', 'version'),)", 'object_name': 'Repository'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'attributes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['server.Attribute']", 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'createpackages': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'createpackages'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['server.Package']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'excludes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'ExcludeAttribute'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['server.Attribute']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'packages': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['server.Package']", 'null': 'True', 'blank': 'True'}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Schedule']", 'null': 'True', 'blank': 'True'}),
            'toinstall': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'toremove': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Version']"})
        },
        'server.schedule': {
            'Meta': {'object_name': 'Schedule'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'server.scheduledelay': {
            'Meta': {'unique_together': "(('schedule', 'delay'),)", 'object_name': 'ScheduleDelay'},
            'attributes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['server.Attribute']", 'null': 'True', 'blank': 'True'}),
            'delay': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Schedule']"})
        },
        'server.store': {
            'Meta': {'unique_together': "(('name', 'version'),)", 'object_name': 'Store'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Version']"})
        },
        'server.update': {
            'Meta': {'object_name': 'Update'},
            'computer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Computer']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Version']"})
        },
        'server.user': {
            'Meta': {'object_name': 'User'},
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'server.userprofile': {
            'Meta': {'object_name': 'UserProfile', '_ormbases': ['auth.User']},
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Version']"})
        },
        'server.version': {
            'Meta': {'object_name': 'Version'},
            'autoregister': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'base': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'computerbase': ('django.db.models.fields.CharField', [], {'default': "'---'", 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'platform': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pms': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Pms']"})
        }
    }

    complete_apps = ['server']
