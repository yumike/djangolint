# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'User'
        db.create_table('oauth_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('github_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('github_access_token', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=255)),
        ))
        db.send_create_signal('oauth', ['User'])


    def backwards(self, orm):
        
        # Deleting model 'User'
        db.delete_table('oauth_user')


    models = {
        'oauth.user': {
            'Meta': {'object_name': 'User'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'github_access_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'github_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['oauth']
