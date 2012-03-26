# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        #This is also done in a custom manner to workwith the latin1 varchar country foreign key
        #like im migration 0007
        db.execute_many("""
        CREATE TABLE `sqp_questionbulkassignments_users` (
            `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
            `questionbulkassignments_id` integer NOT NULL,
            `user_id` integer NOT NULL,
            UNIQUE (`questionbulkassignments_id`, `user_id`)
        ) ENGINE = InnoDB DEFAULT CHARSET = latin1;
        
        ALTER TABLE `sqp_questionbulkassignments_users` ADD CONSTRAINT `user_id_refs_id_
        178ee5d9` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
        """)
        
        db.execute("""
        CREATE TABLE `sqp_questionbulkassignments` (
            `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
            `study_id` integer NULL,
            `country_id` varchar(2) NULL,
            `language_id` integer NULL,
            `can_edit_text` bool NOT NULL,
            `can_edit_details` bool NOT NULL,
            `run_on_save` bool NOT NULL,
            `has_been_run` bool NOT NULL,
            `last_run_date` date NULL
        ) ENGINE = InnoDB DEFAULT CHARSET = latin1;
        """)
        
        db.execute("""
        ALTER TABLE `sqp_questionbulkassignments` ADD CONSTRAINT `country_id_refs_iso_64c7b67d` 
        FOREIGN KEY (`country_id`) REFERENCES `sqp_country` (`iso`);
        """)
        
        db.execute("""
        ALTER TABLE `sqp_questionbulkassignments` ADD CONSTRAINT `language_id_refs_id_7797b23c`
        FOREIGN KEY (`language_id`) REFERENCES `sqp_language` (`id`);
        """)
        
        db.execute("""
        ALTER TABLE `sqp_questionbulkassignments_users` ADD CONSTRAINT `questionbulkassignments_id_refs_id_32707ecc`
         FOREIGN KEY (`questionbulkassignments_id`) REFERENCES 
         `sqp_questionbulkassignments` (`id`);
        """)

        db.send_create_signal('sqp', ['QuestionBulkAssignments'])
        
        # Changing field 'UserProfile.user'
        db.alter_column('sqp_userprofile', 'user_id', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, to=orm['auth.User']))

        # Adding unique constraint on 'UserProfile', fields ['user']
        db.create_unique('sqp_userprofile', ['user_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'UserProfile', fields ['user']
        db.delete_unique('sqp_userprofile', ['user_id'])

        # Deleting model 'QuestionBulkAssignments'
        db.delete_table('sqp_questionbulkassignments')

        # Removing M2M table for field users on 'QuestionBulkAssignments'
        db.delete_table('sqp_questionbulkassignments_users')

        # Changing field 'UserProfile.user'
        db.alter_column('sqp_userprofile', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))


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
        'sqp.branch': {
            'Meta': {'ordering': "('label__characteristic__name', 'label__id')", 'object_name': 'Branch'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Label']"}),
            'to_characteristic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Characteristic']"})
        },
        'sqp.characteristic': {
            'Meta': {'ordering': "['name']", 'object_name': 'Characteristic'},
            'auto_fill_suggestion': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'desc': ('django.db.models.fields.TextField', [], {'db_column': "'description'", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'suggestion': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'validation_rules': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sqp.ValidationRule']", 'null': 'True', 'blank': 'True'}),
            'widget': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Widget']"})
        },
        'sqp.characteristicset': {
            'Meta': {'ordering': "['id']", 'object_name': 'CharacteristicSet'},
            'branches': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sqp.Branch']", 'symmetrical': 'False'}),
            'coders': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sqp.coding': {
            'Meta': {'ordering': "['user', 'characteristic']", 'object_name': 'Coding'},
            'characteristic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Characteristic']"}),
            'choice': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Question']"}),
            'seconds_taken': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'sqp.codingchange': {
            'Meta': {'object_name': 'CodingChange'},
            'change_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'change_by_user_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'change_type': ('django.db.models.fields.IntegerField', [], {}),
            'characteristic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Characteristic']"}),
            'coding_change_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.CodingChangeGroup']"}),
            'coding_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'coding_user_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'error_occured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_value': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'new_value_by_related_country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Country']", 'null': 'True', 'blank': 'True'}),
            'new_value_by_related_lang': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Language']", 'null': 'True', 'blank': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'processing_log': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'question_id': ('django.db.models.fields.IntegerField', [], {})
        },
        'sqp.codingchangegroup': {
            'Meta': {'ordering': "['id']", 'object_name': 'CodingChangeGroup'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'sqp.codingsuggestion': {
            'Meta': {'object_name': 'CodingSuggestion'},
            'characteristic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Characteristic']"}),
            'explanation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Question']"}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'sqp.completion': {
            'Meta': {'object_name': 'Completion'},
            'characteristic_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.CharacteristicSet']"}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'out_of_date': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Question']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'sqp.country': {
            'Meta': {'ordering': "['name']", 'object_name': 'Country'},
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'}),
            'iso_three': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'sqp.faq': {
            'Meta': {'object_name': 'FAQ'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            'asker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.TextField', [], {})
        },
        'sqp.history': {
            'Meta': {'object_name': 'History'},
            'action_description': ('django.db.models.fields.TextField', [], {}),
            'action_type': ('django.db.models.fields.IntegerField', [], {}),
            'actor': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'object_model': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'object_name': ('django.db.models.fields.CharField', [], {'max_length': '170'}),
            'previous_values': ('django.db.models.fields.TextField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'sqp.item': {
            'Meta': {'ordering': "('study', 'admin_letter', 'admin_number', 'id')", 'object_name': 'Item'},
            'admin': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'admin_letter': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'admin_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_item_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'study': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Study']"})
        },
        'sqp.label': {
            'Meta': {'ordering': "('characteristic__name', 'id')", 'object_name': 'Label'},
            'characteristic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Characteristic']"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'compute': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'True'", 'max_length': '150'})
        },
        'sqp.language': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Language'},
            'coders': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'iso2': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sqp.question': {
            'Meta': {'ordering': "('item__study', 'country', 'language', 'item__admin_letter', 'item__admin_number', 'item__id')", 'object_name': 'Question'},
            'answer_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Country']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_question_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduction_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Item']"}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Language']"}),
            'rfa_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'sqp.questionbulkassignments': {
            'Meta': {'object_name': 'QuestionBulkAssignments'},
            'can_edit_details': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'can_edit_text': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Country']", 'blank': 'True'}),
            'has_been_run': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Language']", 'blank': 'True'}),
            'last_run_date': ('django.db.models.fields.DateField', [], {}),
            'run_on_save': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'study': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Study']", 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        },
        'sqp.study': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Study'},
            'coders': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_study_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '70'})
        },
        'sqp.usedcountry': {
            'Meta': {'ordering': "['name']", 'object_name': 'UsedCountry', 'db_table': "'vw_country_question'"},
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'sqp.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'default_characteristic_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.CharacteristicSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_trusted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'sqp.userquestion': {
            'Meta': {'object_name': 'UserQuestion'},
            'can_edit_details': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_edit_text': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Question']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'sqp.validationrule': {
            'Meta': {'object_name': 'ValidationRule'},
            'failure_message': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'rule': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '7'})
        },
        'sqp.widget': {
            'Meta': {'object_name': 'Widget'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['sqp']
