# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from sqp import models as sqp_models
from django.conf import settings


class Migration(DataMigration):

    def forwards(self, orm):
        headers = False
        file = open(settings.PROJECT_DIR + '/data/codes/Old-experiments.csv', 'r')


        def getitems(line, sep=','):
            return line.replace('\n', '').replace('"', '').split(sep)

        missed_rows = []
        OK = 0

        n = 0

        for line in file:
            n +=1
            if n > 50:
                break



            if not headers:
                headers = getitems(line)
                print headers
                continue

            row = dict(zip(headers, getitems(line)))


            study    = sqp_models.Study.objects.get_or_create(name=row['study'])[0]
            item     = sqp_models.Item.objects.get_or_create(name=row['item_name'], study=study)[0]
            language = sqp_models.Language.objects.get(iso=row['language'])
            country  = sqp_models.Country.objects.get(iso=row['country'])



            for key in row.keys():
                if row[key] == 'NA':
                    row[key] = None

            try:
                try:
                    question = sqp_models.Question.objects.get(item=item,
                        language=language,
                        country=country)
                except sqp_models.Question.DoesNotExist:
                    question = sqp_models.Question(item=item,
                        language=language,
                        country=country)

                question.val=row['val']
                question.valz=row['val.est']
                question.val_lo=row['val.lo']
                question.val_hi=row['val.hi']
                question.rel=row['rel']
                question.relz=row['rel.est']
                question.rel_hi=row['rel.hi']
                question.rel_lo=row['rel.lo']


                print question
                question.save(create_suggestions=False)
                print '------------------------------------------------'


                try:
                    user = User.objects.get(username='Old Coder')
                except ObjectDoesNotExist:
                    user = User.objects.create_user('Old Coder', 'none@noreply.com', 'abcdefg')


                for key in row.keys():

                    value = row[key]

                    #skip values that are NA - Not Available
                    if value == None:
                        continue

                    #skip non characteristic keys
                    if key in  [     'study',
                                     'country',
                                     'val',
                                     'val.est',
                                     'val.est.orig',
                                     'val.hi',
                                     'val.lo',
                                     'val.se',
                                     'rel',
                                     'rel.est',
                                     'rel.est.orig',
                                     'rel.hi',
                                     'rel.lo',
                                     'rel.se',
                                     'language',
                                     'item_name',
                                     ]:
                        continue

                    char = getch(key)
                    if char is not None:
                        coding, created = sqp_models.Coding.objects.get_or_create(question=question,
                            characteristic=char,
                            choice = value,
                            user = user)
                        if created:
                            coding.save()
                            #print coding

                    else:
                        if key not in missed_chars:
                            missed_chars.append(key)
                            #print '%s' % key

                #Here the coding is never complete since there are no position / comp_asisted etc...
                question.set_completion(user=user, charset=char_set, complete=False, authorized=True)
                #print 'OK %s' % question
                OK += 1

            except Exception as e:
                error = "MISSED  '%s' '%s' '%s' '%s' Exception %s" %\
                        (row['study'], row['country'], row['language'], row['item_name'], e)
                #print error
                missed_rows.append(error)

        print 'MISSED ROWS %s' % missed_rows
        print 'MISSED CHARS %s' % missed_chars


        print "MISSED %s, OK %s" % (len(missed_rows), OK)


    def backwards(self, orm):
        "Write your backwards methods here."


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
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
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
            'authorized': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'characteristic_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.CharacteristicSet']"}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'out_of_date': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'potential_improvements': ('sqp.fields.PickledObjectField', [], {'null': 'True', 'blank': 'True'}),
            'predictions': ('sqp.fields.PickledObjectField', [], {'null': 'True', 'blank': 'True'}),
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
        'sqp.itemgroup': {
            'Meta': {'object_name': 'ItemGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sqp.Item']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
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
        'sqp.parameter': {
            'Meta': {'ordering': "['order']", 'object_name': 'Parameter'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sqp.View']", 'through': "orm['sqp.Prediction']", 'symmetrical': 'False'})
        },
        'sqp.prediction': {
            'Meta': {'object_name': 'Prediction'},
            'function_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'paramater': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Parameter']"}),
            'view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.View']"})
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
            'rel': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'rel_hi': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'rel_lo': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'relz': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'relz_se': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'rfa_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'val': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'val_hi': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'val_lo': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'valz': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'valz_se': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'sqp.questionbulkassignments': {
            'Meta': {'object_name': 'QuestionBulkAssignments'},
            'assignments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sqp.UserQuestion']", 'symmetrical': 'False', 'blank': 'True'}),
            'can_edit_details': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_edit_text': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Country']", 'null': 'True'}),
            'has_been_run': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.ItemGroup']", 'null': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Language']", 'null': 'True'}),
            'last_run_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        },
        'sqp.questionbulkcreation': {
            'Meta': {'object_name': 'QuestionBulkCreation'},
            'copy_text_from_study': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Study']", 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Country']"}),
            'created_questions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sqp.Question']", 'symmetrical': 'False', 'blank': 'True'}),
            'has_been_run': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.ItemGroup']"}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sqp.Language']"}),
            'last_run_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'sqp.study': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Study'},
            'coders': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
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
        'sqp.view': {
            'Meta': {'ordering': "['order']", 'object_name': 'View'},
            'expects': ('django.db.models.fields.CharField', [], {'default': "'tuple'", 'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '140'})
        },
        'sqp.widget': {
            'Meta': {'object_name': 'Widget'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['sqp']
