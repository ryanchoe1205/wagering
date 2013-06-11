# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Game.team_a_aux_info_1'
        db.add_column(u'game_database_game', 'team_a_aux_info_1',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=144),
                      keep_default=False)

        # Adding field 'Game.team_a_score'
        db.add_column(u'game_database_game', 'team_a_score',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Game.team_b_aux_info_1'
        db.add_column(u'game_database_game', 'team_b_aux_info_1',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=144),
                      keep_default=False)

        # Adding field 'Game.team_b_score'
        db.add_column(u'game_database_game', 'team_b_score',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Game.team_a_aux_info_1'
        db.delete_column(u'game_database_game', 'team_a_aux_info_1')

        # Deleting field 'Game.team_a_score'
        db.delete_column(u'game_database_game', 'team_a_score')

        # Deleting field 'Game.team_b_aux_info_1'
        db.delete_column(u'game_database_game', 'team_b_aux_info_1')

        # Deleting field 'Game.team_b_score'
        db.delete_column(u'game_database_game', 'team_b_score')


    models = {
        u'game_database.game': {
            'Meta': {'object_name': 'Game'},
            'game_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'outcome': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'team_a': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'team_a_aux_info_1': ('django.db.models.fields.CharField', [], {'max_length': '144'}),
            'team_a_score': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'team_b': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'team_b_aux_info_1': ('django.db.models.fields.CharField', [], {'max_length': '144'}),
            'team_b_score': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        }
    }

    complete_apps = ['game_database']