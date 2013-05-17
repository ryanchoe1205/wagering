# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Game'
        db.create_table(u'game_database_game', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('team_a', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('team_b', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('is_finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('outcome', self.gf('django.db.models.fields.CharField')(max_length=5)),
        ))
        db.send_create_signal(u'game_database', ['Game'])


    def backwards(self, orm):
        # Deleting model 'Game'
        db.delete_table(u'game_database_game')


    models = {
        u'game_database.game': {
            'Meta': {'object_name': 'Game'},
            'game_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'outcome': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'team_a': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'team_b': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        }
    }

    complete_apps = ['game_database']