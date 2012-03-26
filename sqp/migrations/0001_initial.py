# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Widget'
        db.create_table('sqp_widget', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('sqp', ['Widget'])

        # Adding model 'ValidationRule'
        db.create_table('sqp_validationrule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('rule', self.gf('django.db.models.fields.TextField')()),
            ('failure_message', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=7)),
        ))
        db.send_create_signal('sqp', ['ValidationRule'])

        # Adding model 'Characteristic'
        db.create_table('sqp_characteristic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('desc', self.gf('django.db.models.fields.TextField')(db_column='description', blank=True)),
            ('widget', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sqp.Widget'])),
            ('suggestion', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('sqp', ['Characteristic'])

        # Adding M2M table for field validation_rules on 'Characteristic'
        db.create_table('sqp_characteristic_validation_rules', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('characteristic', models.ForeignKey(orm['sqp.characteristic'], null=False)),
            ('validationrule', models.ForeignKey(orm['sqp.validationrule'], null=False))
        ))
        db.create_unique('sqp_characteristic_validation_rules', ['characteristic_id', 'validationrule_id'])

        # Adding model 'Label'
        db.create_table('sqp_label', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='True', max_length=150)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('characteristic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sqp.Characteristic'])),
            ('compute', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('sqp', ['Label'])

        # Adding model 'Branch'
        db.create_table('sqp_branch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sqp.Label'])),
            ('to_characteristic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sqp.Characteristic'])),
        ))
        db.send_create_signal('sqp', ['Branch'])

        # Adding model 'CharacteristicSet'
        db.create_table('sqp_characteristicset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('sqp', ['CharacteristicSet'])

        # Adding M2M table for field branches on 'CharacteristicSet'
        db.create_table('sqp_characteristicset_branches', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('characteristicset', models.ForeignKey(orm['sqp.characteristicset'], null=False)),
            ('branch', models.ForeignKey(orm['sqp.branch'], null=False))
        ))
        db.create_unique('sqp_characteristicset_branches', ['characteristicset_id', 'branch_id'])

        # Adding M2M table for field coders on 'CharacteristicSet'
        db.create_table('sqp_characteristicset_coders', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('characteristicset', models.ForeignKey(orm['sqp.characteristicset'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('sqp_characteristicset_coders', ['characteristicset_id', 'user_id'])

        # Adding model 'Study'
        db.create_table('sqp_study', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=70)),
        ))
        db.send_create_signal('sqp', ['Study'])

        # Adding M2M table for field coders on 'Study'
        db.create_table('sqp_study_coders', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('study', models.ForeignKey(orm['sqp.study'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('sqp_study_coders', ['study_id', 'user_id'])

        # Adding model 'Item'
        db.create_table('sqp_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('admin', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('long_name', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('study', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sqp.Study'])),
            ('admin_letter', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('admin_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('sqp', ['Item'])

        # Adding model 'Language'
        db.create_table('sqp_language', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('iso', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('iso2', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
        ))
        db.send_create_signal('sqp', ['Language'])

        # Adding M2M table for field coders on 'Language'
        db.create_table('sqp_language_coders', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('language', models.ForeignKey(orm['sqp.language'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('sqp_language_coders', ['language_id', 'user_id'])

        # Adding model 'Country'
        db.create_table('sqp_country', (
            ('iso', self.gf('django.db.models.fields.CharField')(max_length=2, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('iso_three', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
        ))
        db.send_create_signal('sqp', ['Country'])

        # Adding model 'Question'
        db.create_table('sqp_question', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sqp.Item'])),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sqp.Language'])),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sqp.Country'])),
            ('introduction_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('rfa_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('answer_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('sqp', ['Question'])

        # Adding model 'Coding'
        db.create_table('sqp_coding', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sqp.Question'])),
            ('characteristic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sqp.Characteristic'])),
            ('choice', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')()),
            ('seconds_taken', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('sqp', ['Coding'])

        # Adding model 'UsedCountry'
        db.create_table('vw_country_question', (
            ('iso', self.gf('django.db.models.fields.CharField')(max_length=2, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('sqp', ['UsedCountry'])

        # Adding model 'Completion'
        db.create_table('sqp_completion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sqp.Question'])),
            ('characteristic_set', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sqp.CharacteristicSet'])),
            ('complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('sqp', ['Completion'])

        # Adding model 'FAQ'
        db.create_table('sqp_faq', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('question', self.gf('django.db.models.fields.TextField')()),
            ('answer', self.gf('django.db.models.fields.TextField')()),
            ('date_added', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('sqp', ['FAQ'])


    def backwards(self, orm):
        pass

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
        'sqp.completion': {
            'Meta': {'object_name': 'Completion'},
            'characteristic_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.CharacteristicSet']"}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        'sqp.item': {
            'Meta': {'ordering': "('study', 'admin_letter', 'admin_number', 'id')", 'object_name': 'Item'},
            'admin': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'admin_letter': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'admin_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduction_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Item']"}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Language']"}),
            'rfa_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'sqp.study': {
            'Meta': {'object_name': 'Study'},
            'coders': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '70'})
        },
        'sqp.usedcountry': {
            'Meta': {'ordering': "['name']", 'object_name': 'UsedCountry', 'db_table': "'vw_country_question'"},
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
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
