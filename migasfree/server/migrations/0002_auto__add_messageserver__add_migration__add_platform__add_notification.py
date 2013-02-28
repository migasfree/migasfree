# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from migasfree.server.models import Platform
from migasfree.server.models import Update
from migasfree.server.models import Migration as Mig
from django.db.models import Min


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MessageServer'
        db.create_table('server_messageserver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
        ))
        db.send_create_signal('server', ['MessageServer'])

        # Adding model 'Migration'
        db.create_table('server_migration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('computer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Computer'])),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Version'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
        ))
        db.send_create_signal('server', ['Migration'])

        #insert Migrations
        qry = Update.objects.values('computer', 'version').annotate(date=Min('date'))
        for q in qry:
            o_migration = Mig()
            o_migration.computer_id = q.get('computer')
            o_migration.version_id = q.get('version')
            o_migration.date = q.get('date')
            o_migration.save()

        # Adding model 'Platform'
        db.create_table('server_platform', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('server', ['Platform'])


        #insert Platforms
        o_Platform=Platform()
        o_Platform.id=1
        o_Platform.name="Windows"
        o_Platform.save()

        o_Platform=Platform()
        o_Platform.id=2
        o_Platform.name="Linux"
        o_Platform.save()


        # Adding model 'Notification'
        db.create_table('server_notification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('notification', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('checked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('server', ['Notification'])

        # Deleting field 'Property.after_insert'
        db.delete_column('server_property', 'after_insert')

        # Deleting field 'Property.before_insert'
        db.delete_column('server_property', 'before_insert')


        # Renaming column for 'Version.platform' to match new field type.
        db.rename_column('server_version', 'platform', 'platform_id')
        # Changing field 'Version.platform'
        db.alter_column('server_version', 'platform_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Platform']))
        # Adding index on 'Version', fields ['platform']
        db.create_index('server_version', ['platform_id'])

        # Adding field 'Computer.datehardware'
        db.add_column('server_computer', 'datehardware',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)

        # Adding field 'Checking.alert'
        db.add_column('server_checking', 'alert',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


        # Changing field 'Update.version'
        db.alter_column('server_update', 'version_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Version'], null=True))

        # Changing field 'Message.text'
        db.alter_column('server_message', 'text', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'UserProfile.version'
        db.alter_column('server_userprofile', 'version_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['server.Version'], null=True))

    def backwards(self, orm):
        # Removing index on 'Version', fields ['platform']
        db.delete_index('server_version', ['platform_id'])

        # Deleting model 'MessageServer'
        db.delete_table('server_messageserver')

        # Deleting model 'Migration'
        db.delete_table('server_migration')

        # Deleting model 'Platform'
        db.delete_table('server_platform')

        # Deleting model 'Notification'
        db.delete_table('server_notification')

        # Adding field 'Property.after_insert'
        db.add_column('server_property', 'after_insert',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Property.before_insert'
        db.add_column('server_property', 'before_insert',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


        # Renaming column for 'Version.platform' to match new field type.
        db.rename_column('server_version', 'platform_id', 'platform')
        # Changing field 'Version.platform'
        db.alter_column('server_version', 'platform', self.gf('django.db.models.fields.IntegerField')())
        # Deleting field 'Computer.datehardware'
        db.delete_column('server_computer', 'datehardware')

        # Deleting field 'Checking.alert'
        db.delete_column('server_checking', 'alert')


        # Changing field 'Update.version'
        db.alter_column('server_update', 'version_id', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['server.Version']))

        # Changing field 'Message.text'
        db.alter_column('server_message', 'text', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'UserProfile.version'
        db.alter_column('server_userprofile', 'version_id', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['server.Version']))

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
            'alert': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'server.computer': {
            'Meta': {'object_name': 'Computer'},
            'datehardware': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
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
            'repository': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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
