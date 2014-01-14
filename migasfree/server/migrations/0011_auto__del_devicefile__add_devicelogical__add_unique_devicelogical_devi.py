# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'DeviceFile'
        db.delete_table('server_devicefile')

        # Adding model 'DeviceLogical'
        db.create_table('server_devicelogical', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Device'])),
            ('feature', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.DeviceFeature'])),
        ))
        db.send_create_signal('server', ['DeviceLogical'])

        # Adding unique constraint on 'DeviceLogical', fields ['device', 'feature']
        db.create_unique('server_devicelogical', ['device_id', 'feature_id'])

        # Adding model 'DeviceDriver'
        db.create_table('server_devicedriver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.DeviceModel'])),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Version'])),
            ('feature', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.DeviceFeature'])),
            ('install', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('server', ['DeviceDriver'])

        # Adding unique constraint on 'DeviceDriver', fields ['model', 'version', 'feature']
        db.create_unique('server_devicedriver', ['model_id', 'version_id', 'feature_id'])

        # Adding model 'DeviceFeature'
        db.create_table('server_devicefeature', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('server', ['DeviceFeature'])

        # Deleting field 'Device.alias'
        db.delete_column('server_device', 'alias')

        # Deleting field 'Device.location'
        db.delete_column('server_device', 'location')

        # Deleting field 'Device.information'
        db.delete_column('server_device', 'information')

        # Deleting field 'Device.uri'
        db.delete_column('server_device', 'uri')

        # Adding field 'Device.data'
        db.add_column('server_device', 'data', self.gf('django.db.models.fields.TextField')(default='{}', null=True), keep_default=False)

        # Deleting field 'DeviceModel.postinstall'
        db.delete_column('server_devicemodel', 'postinstall')

        # Deleting field 'DeviceModel.preremove'
        db.delete_column('server_devicemodel', 'preremove')

        # Deleting field 'DeviceModel.preinstall'
        db.delete_column('server_devicemodel', 'preinstall')

        # Deleting field 'DeviceModel.devicefile'
        db.delete_column('server_devicemodel', 'devicefile_id')

        # Deleting field 'DeviceModel.postremove'
        db.delete_column('server_devicemodel', 'postremove')

        # Deleting field 'Computer.devices_modified'
        db.delete_column('server_computer', 'devices_modified')

        # Removing M2M table for field devices on 'Computer'
        db.delete_table('server_computer_devices')

        # Adding M2M table for field devices_logical on 'Computer'
        db.create_table('server_computer_devices_logical', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('computer', models.ForeignKey(orm['server.computer'], null=False)),
            ('devicelogical', models.ForeignKey(orm['server.devicelogical'], null=False))
        ))
        db.create_unique('server_computer_devices_logical', ['computer_id', 'devicelogical_id'])

        # Deleting field 'Pms.repository'
        db.delete_column('server_pms', 'repository')

        # Deleting field 'DeviceConnection.install'
        db.delete_column('server_deviceconnection', 'install')

        # Deleting field 'DeviceConnection.remove'
        db.delete_column('server_deviceconnection', 'remove')

        # Deleting field 'DeviceConnection.uri'
        db.delete_column('server_deviceconnection', 'uri')

        # Changing field 'DeviceConnection.fields'
        db.alter_column('server_deviceconnection', 'fields', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))


    def backwards(self, orm):
        
        # Removing unique constraint on 'DeviceDriver', fields ['model', 'version', 'feature']
        db.delete_unique('server_devicedriver', ['model_id', 'version_id', 'feature_id'])

        # Removing unique constraint on 'DeviceLogical', fields ['device', 'feature']
        db.delete_unique('server_devicelogical', ['device_id', 'feature_id'])

        # Adding model 'DeviceFile'
        db.create_table('server_devicefile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('server', ['DeviceFile'])

        # Deleting model 'DeviceLogical'
        db.delete_table('server_devicelogical')

        # Deleting model 'DeviceDriver'
        db.delete_table('server_devicedriver')

        # Deleting model 'DeviceFeature'
        db.delete_table('server_devicefeature')

        # Adding field 'Device.alias'
        db.add_column('server_device', 'alias', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True), keep_default=False)

        # Adding field 'Device.location'
        db.add_column('server_device', 'location', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50, null=True, blank=True), keep_default=False)

        # Adding field 'Device.information'
        db.add_column('server_device', 'information', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50, null=True, blank=True), keep_default=False)

        # Adding field 'Device.uri'
        db.add_column('server_device', 'uri', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50, null=True, blank=True), keep_default=False)

        # Deleting field 'Device.data'
        db.delete_column('server_device', 'data')

        # Adding field 'DeviceModel.postinstall'
        db.add_column('server_devicemodel', 'postinstall', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'DeviceModel.preremove'
        db.add_column('server_devicemodel', 'preremove', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'DeviceModel.preinstall'
        db.add_column('server_devicemodel', 'preinstall', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'DeviceModel.devicefile'
        db.add_column('server_devicemodel', 'devicefile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.DeviceFile'], null=True, blank=True), keep_default=False)

        # Adding field 'DeviceModel.postremove'
        db.add_column('server_devicemodel', 'postremove', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Computer.devices_modified'
        db.add_column('server_computer', 'devices_modified', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding M2M table for field devices on 'Computer'
        db.create_table('server_computer_devices', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('computer', models.ForeignKey(orm['server.computer'], null=False)),
            ('device', models.ForeignKey(orm['server.device'], null=False))
        ))
        db.create_unique('server_computer_devices', ['computer_id', 'device_id'])

        # Removing M2M table for field devices_logical on 'Computer'
        db.delete_table('server_computer_devices_logical')

        # Adding field 'Pms.repository'
        db.add_column('server_pms', 'repository', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'DeviceConnection.install'
        db.add_column('server_deviceconnection', 'install', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'DeviceConnection.remove'
        db.add_column('server_deviceconnection', 'remove', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'DeviceConnection.uri'
        db.add_column('server_deviceconnection', 'uri', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True), keep_default=False)

        # Changing field 'DeviceConnection.fields'
        db.alter_column('server_deviceconnection', 'fields', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 3, 13, 0, 53, 198407)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 3, 13, 0, 53, 198280)'}),
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
            'alert': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'server.computer': {
            'Meta': {'object_name': 'Computer'},
            'datehardware': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dateinput': ('django.db.models.fields.DateField', [], {}),
            'datelastupdate': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'devices_copy': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'devices_logical': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['server.DeviceLogical']", 'null': 'True', 'blank': 'True'}),
            'history_sw': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'software': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['server.Attribute']", 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Version']"})
        },
        'server.device': {
            'Meta': {'unique_together': "(('connection', 'name'),)", 'object_name': 'Device'},
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.DeviceConnection']"}),
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.DeviceModel']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'server.deviceconnection': {
            'Meta': {'unique_together': "(('devicetype', 'name'),)", 'object_name': 'DeviceConnection'},
            'devicetype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.DeviceType']"}),
            'fields': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'server.devicedriver': {
            'Meta': {'unique_together': "(('model', 'version', 'feature'),)", 'object_name': 'DeviceDriver'},
            'feature': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.DeviceFeature']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'install': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.DeviceModel']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Version']"})
        },
        'server.devicefeature': {
            'Meta': {'object_name': 'DeviceFeature'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'server.devicelogical': {
            'Meta': {'unique_together': "(('device', 'feature'),)", 'object_name': 'DeviceLogical'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Device']"}),
            'feature': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.DeviceFeature']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'server.devicemanufacturer': {
            'Meta': {'object_name': 'DeviceManufacturer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'server.devicemodel': {
            'Meta': {'unique_together': "(('devicetype', 'manufacturer', 'name'),)", 'object_name': 'DeviceModel'},
            'connections': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['server.DeviceConnection']", 'null': 'True', 'blank': 'True'}),
            'devicetype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.DeviceType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.DeviceManufacturer']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
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
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['server.UserProfile']", 'null': 'True', 'blank': 'True'})
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
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'server.messageserver': {
            'Meta': {'object_name': 'MessageServer'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'server.migration': {
            'Meta': {'object_name': 'Migration'},
            'computer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Computer']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Version']"})
        },
        'server.notification': {
            'Meta': {'object_name': 'Notification'},
            'checked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notification': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'server.package': {
            'Meta': {'unique_together': "(('name', 'version'),)", 'object_name': 'Package'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Store']"}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Version']"})
        },
        'server.platform': {
            'Meta': {'object_name': 'Platform'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'server.pms': {
            'Meta': {'object_name': 'Pms'},
            'createrepo': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'slug': ('django.db.models.fields.CharField', [], {'default': "'REPOSITORIES'", 'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'server.property': {
            'Meta': {'object_name': 'Property'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'auto': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'language': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'prefix': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'tag': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
            'date': ('django.db.models.fields.DateField', [], {}),
            'defaultexclude': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'defaultinclude': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'defaultpreinclude': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'excludes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'ExcludeAttribute'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['server.Attribute']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.User']"}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Version']", 'null': 'True'})
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
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Version']", 'null': 'True'})
        },
        'server.version': {
            'Meta': {'object_name': 'Version'},
            'autoregister': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'base': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'computerbase': ('django.db.models.fields.CharField', [], {'default': "'---'", 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'platform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Platform']"}),
            'pms': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['server.Pms']"})
        }
    }

    complete_apps = ['server']
