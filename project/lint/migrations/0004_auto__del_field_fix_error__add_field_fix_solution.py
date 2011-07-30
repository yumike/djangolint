# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Fix.error'
        db.delete_column('lint_fix', 'error')

        # Adding field 'Fix.solution'
        db.add_column('lint_fix', 'solution', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'Fix.error'
        raise RuntimeError("Cannot reverse this migration. 'Fix.error' and its values cannot be restored.")

        # Deleting field 'Fix.solution'
        db.delete_column('lint_fix', 'solution')


    models = {
        'lint.fix': {
            'Meta': {'object_name': 'Fix'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fixes'", 'to': "orm['lint.Report']"}),
            'solution': ('django.db.models.fields.TextField', [], {}),
            'source': ('django.db.models.fields.TextField', [], {})
        },
        'lint.report': {
            'Meta': {'ordering': "['-created_on']", 'object_name': 'Report'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'error': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stage': ('django.db.models.fields.CharField', [], {'default': "'waiting'", 'max_length': '10'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['lint']
