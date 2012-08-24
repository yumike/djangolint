# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Commit'
        db.create_table('webhooks_commit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('repo_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('repo_user', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ref', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('compare_url', self.gf('django.db.models.fields.URLField')(max_length=255)),
            ('committer_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('committer_email', self.gf('django.db.models.fields.EmailField')(max_length=255)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('webhooks', ['Commit'])

        # Adding unique constraint on 'Commit', fields ['hash', 'repo_name', 'repo_user']
        db.create_unique('webhooks_commit', ['hash', 'repo_name', 'repo_user'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Commit', fields ['hash', 'repo_name', 'repo_user']
        db.delete_unique('webhooks_commit', ['hash', 'repo_name', 'repo_user'])

        # Deleting model 'Commit'
        db.delete_table('webhooks_commit')


    models = {
        'webhooks.commit': {
            'Meta': {'ordering': "['-created_on']", 'unique_together': "(['hash', 'repo_name', 'repo_user'],)", 'object_name': 'Commit'},
            'committer_email': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'committer_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'compare_url': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'ref': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'repo_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'repo_user': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['webhooks']
