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
            ('identificator', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=255)),
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('oauth', ['User'])


    def backwards(self, orm):
        
        # Deleting model 'User'
        db.delete_table('oauth_user')


    models = {
        'oauth.user': {
            'Meta': {'object_name': 'User'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identificator': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['oauth']
