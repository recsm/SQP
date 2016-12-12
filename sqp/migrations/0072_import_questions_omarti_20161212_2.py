# encoding: utf-8
import os
import datetime
import re
import codecs

from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.conf import settings
from sqp import models as sqp_models

class Migration(DataMigration):

    def forwards(self, orm):

        try:
            sql = 'ALTER TABLE sqp_item DROP INDEX unique_name;'
            db.execute_many(sql)
            print "unique_name index dropped"
        except:
            print "unique_name index not dropped (most likely already deleted)"



        log_text = ''

        Q_BASE_DIR  = settings.PROJECT_DIR + '/data/questions_omarti_20161212_2/'
        files = []
        r,d,files = os.walk(Q_BASE_DIR).next()

        #looking for russian A and B chars
        item_regex = re.compile(ur'^(P\.)?[\u0041-\u005A\u0410\u0412\u0421]{1,2}[0-9]{1,3}([A-Za-z\u0410\u0412\u0421\u0430\u0432\u0441]{1,3})?(\.)?$')
        text_area_regex = re.compile(ur'\{[A-Z]+\}')
        q_regex = re.compile(ur'Q{1}[0-9]{1,4}')

        for file_name in sorted(files):
            file_log_text = []
            CREATED_ITEMS = 0
            CREATED_QUESTIONS = 0
            EDITED_QUESTIONS = 0
            NOT_EDITED = 0
            SKIPPED_AREAS = 0
            IMPORTED_LINES = 0
            SKIPPED_LINES = []

            #utf-8-sig to get rid of the utf-8 BOM /ufeff
            #http://stackoverflow.com/questions/9228202/tokenizing-unicode-using-nltk
            file = codecs.open(Q_BASE_DIR + file_name, "r", "utf-8-sig")

            if not '.txt' in file_name:
                continue


            print "NOW CHECKING file %s" % file.name

            params = file_name.replace('.txt', '').split('_')
            if len(params) > 3:
                round_name, country_iso, language_iso, supplemental = file_name.replace('.txt', '').split('_')
            else:
                round_name, country_iso, language_iso = file_name.replace('.txt', '').split('_')


            language = sqp_models.Language.objects.get(iso=language_iso)
            country = sqp_models.Country.objects.get(iso=country_iso)
            round_name = round_name.replace('ESS', 'ESS Round ')
            study = sqp_models.Study.objects.get(name=round_name)

            key = None
            questions = {}
            text_areas = ['INTRO',
                          'QUESTION',
                          'ANSWERS',
                          'TRASH']
            line_number = 0
            for line in file:
                line_number += 1
                #Get rid of any Q13 Q12 crap
                if q_regex.match(line):
                    line = re.sub(q_regex, '', line).strip()
                    key = None
                if item_regex.match(line.strip()):
                    key = item_regex.match(line.strip()).group(0)
                    #russian chars
                    key = key.replace(u'\u0410', 'A')
                    key = key.replace(u'\u0412', 'B')
                    key = key.replace(u'\u0421', 'C')
                    key = key.replace(u'\u0430', 'a')
                    key = key.replace(u'\u0432', 'b')
                    key = key.replace(u'\u0441', 'c')
                                        #P.
                    key = key.replace('P.', '')
                    key = key.replace(' ', '')

                    #Trailing .
                    key = key.replace('.', '')

                    questions[key] = {'INTRO'   : '',
                                      'QUESTION' : '',
                                      'ANSWERS'  : '',
                                      'found_text_areas' : []
                    }

                    current_text_area = 'QUESTION'
                    continue
                elif key and text_area_regex.match(line):
                    match = text_area_regex.match(line).group(0)
                    current_text_area = match.replace('{', '').replace('}', '')

                    if current_text_area == 'ANSWERS 1':
                        current_text_area ='ANSWERS'
                    elif current_text_area == 'ANSWERS 2':
                        SKIPPED_AREAS += 1
                        continue


                    if current_text_area in questions[key]['found_text_areas']:
                        current_text_area = 'TRASH'
                    else:
                        questions[key]['found_text_areas'].append(current_text_area)

                    if current_text_area not in text_areas:
                        raise Exception('Unrecognized text area "%s"' % current_text_area)
                    continue


                #Only take the first occurence of QUESTION / INTRO / ANSWERS
                if key and current_text_area != 'TRASH':
                    questions[key][current_text_area] += line
                    IMPORTED_LINES += 1
                elif line.strip() != '':
                    SKIPPED_LINES.append({'line_number' : line_number,
                                          'content': line})

            n = 0
            for key in questions:
                n +=1
                #if n > 10:break
                #print "NOW SAVING question %s" % key
                try:
                    item, i_was_created = sqp_models.Item.objects.get_or_create(admin=key, study=study)
                    if i_was_created:
                        CREATED_ITEMS += 1
                except Exception as ex:
                    print '!!!!!!!!!!BAD KEY!!!!!!!!!!!!!!!%s' % key
                    file_log_text.append('!!!!!!!!!!BAD KEY!!!!!!!!!!!!!!!%s' % key)
                    #raise Exception()

                question, q_was_created = sqp_models.Question.objects.get_or_create(item=item, country=country, language=language)
                if q_was_created:
                    CREATED_QUESTIONS += 1

                if question.rfa_text or question.introduction_text or question.answer_text:
                    NOT_EDITED += 1
                else:
                    question.introduction_text = questions[key]['INTRO'].strip()
                    question.rfa_text = questions[key]['QUESTION'].strip()
                    question.answer_text = questions[key]['ANSWERS'].strip()

                    if q_was_created:
                        question.imported_from = 'jorge-created'
                    else:
                        question.imported_from = 'jorge-existing'

                    question.save(create_suggestions = False)
                    EDITED_QUESTIONS += 1


            file_log_text.append('%s %s %s new items:%s, total qs:%s, created qs:%s, edited qs:%s, not edited qs:%s, skipped keys:%s' %\
                                 (country_iso, language_iso, round_name,
                                  CREATED_ITEMS, len(questions), CREATED_QUESTIONS, EDITED_QUESTIONS, NOT_EDITED, SKIPPED_AREAS))
            file_log_text.append('LINES SKIPPED %s / IMPORTED %s' % (len(SKIPPED_LINES), IMPORTED_LINES))
            if SKIPPED_LINES:
                file_log_text.append('SKIPPED_LINES')
                for l in SKIPPED_LINES:
                    file_log_text.append('     %s: %s' % (l['line_number'], l['content'].replace('\n', '')))

            file_log_text.append('IMPORTED ITEMS: %s' % ','.join(questions.keys()))
            file_log_text.append('------------------------------------------------------------------------')

            print '\n'.join(file_log_text)
            print
            log_text += '\n'.join(file_log_text) + '\n\n\n'

        log_file = codecs.open('/tmp/omarti_import_20161212_2.log', 'w', "utf-8-sig")
        log_file.write(log_text)
        log_file.close()
        print "LOG STORED AT '/tmp/omarti_import_20161212_2.log'"



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
            'imported_from': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
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
