# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ExifTagSubstitute'
        db.create_table('robinson_exiftagsubstitute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('original_value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('substitute_value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('robinson', ['ExifTagSubstitute'])

    def backwards(self, orm):
        
        # Deleting model 'ExifTagSubstitute'
        db.delete_table('robinson_exiftagsubstitute')

    models = {
        'robinson.exiftag': {
            'Meta': {'unique_together': "(('key', 'photo'),)", 'object_name': 'ExifTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'photo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['robinson.Photo']"}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'robinson.exiftagsubstitute': {
            'Meta': {'object_name': 'ExifTagSubstitute'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'original_value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'substitute_value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
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
