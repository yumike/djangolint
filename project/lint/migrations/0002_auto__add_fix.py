# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Fix'
        db.create_table('lint_fix', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fixes', to=orm['lint.Report'])),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('line', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('source', self.gf('django.db.models.fields.TextField')()),
            ('error', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('lint', ['Fix'])


    def backwards(self, orm):
        
        # Deleting model 'Fix'
        db.delete_table('lint_fix')


    models = {
        'lint.fix': {
            'Meta': {'object_name': 'Fix'},
            'error': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fixes'", 'to': "orm['lint.Report']"}),
            'source': ('django.db.models.fields.TextField', [], {})
        },
        'lint.report': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Report'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'error': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stage': ('django.db.models.fields.CharField', [], {'default': "'waiting'", 'max_length': '10'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['lint']
