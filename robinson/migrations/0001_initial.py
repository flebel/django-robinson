# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ExifTag'
        db.create_table('robinson_exiftag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('photo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['robinson.Photo'])),
        ))
        db.send_create_signal('robinson', ['ExifTag'])

        # Adding unique constraint on 'ExifTag', fields ['key', 'photo']
        db.create_unique('robinson_exiftag', ['key', 'photo_id'])

        # Adding model 'Photo'
        db.create_table('robinson_photo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('location_accuracy', self.gf('django.db.models.fields.SmallIntegerField')(default=110)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('tags', self.gf('tagging.fields.TagField')()),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('estimated_location', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('elevation', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('robinson', ['Photo'])

    def backwards(self, orm):
        
        # Removing unique constraint on 'ExifTag', fields ['key', 'photo']
        db.delete_unique('robinson_exiftag', ['key', 'photo_id'])

        # Deleting model 'ExifTag'
        db.delete_table('robinson_exiftag')

        # Deleting model 'Photo'
        db.delete_table('robinson_photo')

    models = {
        'robinson.exiftag': {
            'Meta': {'unique_together': "(('key', 'photo'),)", 'object_name': 'ExifTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'photo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['robinson.Photo']"}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'robinson.photo': {
            'Meta': {'object_name': 'Photo'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'elevation': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'estimated_location': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'file': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'location_accuracy': ('django.db.models.fields.SmallIntegerField', [], {'default': '110'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {})
        }
    }

    complete_apps = ['robinson']
