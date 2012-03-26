# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings
from sqp import models as sqp_models
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from sqp.views_ui_functions import next_branch

class Migration(SchemaMigration):
    no_dry_run = True

    def forwards(self, orm):
        
        all_chars = [char for char in sqp_models.Characteristic.objects.all()]
        cursor = connection.cursor()

        char_set = sqp_models.CharacteristicSet.objects.get(pk=3)

        def getitems(line, sep=','):
            return line.replace('\n', '').replace('"', '').split(sep)
        
        def getch(shnam): 
            for char in all_chars:
                if char.short_name == shnam:
                    return char
            return None
        
        log_file = open('/tmp/round_1_to_3_import.csv', 'w')
        log_file.write("Question Id\tCountry\tLanguage\tStudy\tItem\tFound DB\tFound Diana\tMTMM Status\tComplete\tSource Question Id\tCopied Source Chars\tTotal Chars\tFirst Missing Char\tException\n")
        log_file.close()
        
        file = open(settings.PROJECT_DIR + '/data/codes/cleaned_codings_diana.csv', 'r')
        line = file.readline()
        
        diana_headers = getitems(line, '\t')
        
        #First we import all of Diana's codings into a table for easy reference
        #so that we can pick up some codings that we need and are unable to determine
        #from the fulljoin file
        create_table_sql = """
            CREATE TABLE cleaned_codings_diana (
             id int(11) NOT NULL AUTO_INCREMENT,
        """
        
        for header in diana_headers:
            create_table_sql += """
             %s varchar(100) NOT NULL,
            """ % header
        
        create_table_sql += """
         PRIMARY KEY (id)
            ) ENGINE=MyISAM DEFAULT CHARSET=latin1;
        """
        try:
            db.execute_many(create_table_sql)
            
            for line in file:
                values = getitems(line, '\t')
                sql = "INSERT INTO cleaned_codings_diana VALUES (NULL, '%s');" % "\',\'".join(values)
                db.execute(sql)
            #Remove the comma from question_id
            #Change to an int type
            #Create an index
            fix_sql = """
            UPDATE  `cleaned_codings_diana`  SET  question_id = REPLACE(question_id, ',', '');
            ALTER TABLE `cleaned_codings_diana` CHANGE `question_id` `question_id` INT NOT NULL;
             
            """   
            db.execute_many(fix_sql)
        except:
            pass
        
        file.close()

        source_language = sqp_models.Language.objects.get(iso='eng')
        source_country = sqp_models.Country.objects.get(iso='GB')
        
        def run_import(eng_only= False):
            
            log_file = open('/tmp/round_1_to_3_import.csv', 'a', 1024)
            
            headers = False
            OK = 0
            MISSED = 0
            
            OK_DIANA = 0
            MISSED_DIANA = 0
            
            COMPLETE = 0
            INCOMPLETE = 0
            
            #i = 0
            missed_rows = []
            
            joinfile = open(settings.PROJECT_DIR + '/data/codes/ESS-codings-mtmm-fulljoin.csv', 'r')
            for line in joinfile:
               
                if not headers:
                    headers = getitems(line)
                    continue
                
                row = dict(zip(headers, getitems(line)))
                
                
                #Remap by name
                row['comp_assist'] = row.pop('computer.assisted')
    
                row_study = row.pop('study')
                row_country = row.pop('country')
                row_language = row.pop('language')
                row_item_name = row.pop('item_name')
                
                #The first run we import source only
                if eng_only:
                    if row_language != 'eng' or row_country != 'GB':
                        continue
                else:
                #The second time we import the others
                    if row_language == 'eng' and row_country == 'GB':
                        continue
                    
                found_db       =  "."
                found_diana    =  "." 
                is_complete       =  "."
                missing_char      =  "."
                exception = "."
                question_id = "."
                source_question_id = "."
                source_row_dict = None
                MTMM_Status = '.'
                total_chars = 0
                
                #Fix a mismatch in the language code variants for Romanian
                #between Daniel's file and the sqp db
                if row_language == 'rum':
                    row_language = 'ron'
                
                daniel_row = row
                
                try:
                    study    = sqp_models.Study.objects.get(name=row_study)
                    item     = sqp_models.Item.objects.get(name=row_item_name, study=study)
                    language = sqp_models.Language.objects.get(iso=row_language)
                    country  = sqp_models.Country.objects.get(iso=row_country)
                    try:
                        question = sqp_models.Question.objects.get(item=item, language=language, country=country)
                        question_id = str(int(question.id))
                        found_db = "DB OK"
                    except:
                        question = sqp_models.Question(item=item, language=language, country=country)
                        question.save()
                        found_db = "DB MISSING (NEW RECORD CREATED)"
                        
                    
                    sql = "SELECT * FROM cleaned_codings_diana WHERE question_id = %s" % question.id
                    
                    cursor.execute(sql)
                    description = [x[0] for x in cursor.description]
                    diana_row = cursor.fetchone()
                    found_diana = "DIANA FILE MISSING"
                    if diana_row is not None:
                        found_diana = "DIANA FILE OK"
                        
                        #Start the row_dict with diana's codes
                        row_dict = dict(zip(description, diana_row))
                        #Then merge in daniels dict
                        for key in daniel_row.keys():
                            
                            if key in ['domain', 'concept']:
                                #Prefer Diana's codes for concept and domain
                                continue
                            
                            row_dict[key] = daniel_row[key]
                        import_codes = True
                    else:
                        row_dict = daniel_row
                        #When there is no row in Diana's file it means no codes exist
                        import_codes = False
                        
                        
                        #Check the MTMM
                    if row_dict['rel.est'] != 'NA':
                        if question.rel:
                            MTMM_Status = 'MTMM OK'
                        else:
                            MTMM_Status = 'MTMM MISSING IN DB'
                            
                    if import_codes:
                        
                    
                        #Diana truncated the usernames to 8 chars so we use startswith
                        user = User.objects.get(username__startswith=row_dict['coder'])
                        
                        try:
                            source_question = sqp_models.Question.objects.get(item=item, language=source_language, country=source_country)
                            source_question_id = str(int(source_question.id))
                            source_row_dict = {}
                            
                            for code in sqp_models.Coding.objects.filter(question=source_question):
                                source_row_dict[code.characteristic.short_name] = code.choice
                            
                            
                        except sqp_models.Question.DoesNotExist:
                            print "NO CORRESPONDING SOURCE FOUND for %s" % question
                            source_question_id = "NONE"
                            pass
    
                       
                            
                        
                                
                        print "Daniel %s Question %s MTMM %s" % (row_dict['rel.est'], question.rel, MTMM_Status)
                        
                        chars_from_source = {'domain' :         None,
                                             'concept' :        None,
                                             'conc_simple':     None,
                                             'conc_complex' :   None,
                                             'natpoldomain':    None,
                                             'dom_family'   :   None,
                                             'dom_work'     :   None,
                                             'dom_leisure'  :   None,
                                             'dom_personal' :   None,
                                             'dom_consumer' :   None,
                                             'dom_health'   :   None,
                                             'dom_backgrou' :   None,
                                             'dom_other'    :   None,
                                             'dom_european' :   None
                                             }
                        
                        for key in row_dict.keys():
                            
                            value = row_dict[key]
                            
                            #skip Not applicable codes
                            #Diana's file uses . and ,
                            #Daniel's file uses NA
                            if value in ['.', ',', 'NA']:
                                continue
                            
                            if key == 'concept' and value == '0':
                                #We consider the value 0 for concept to mean no value available from Diana's cleaned codings
                                continue
                            
                            if key in chars_from_source.keys():
                                chars_from_source[key] = value
                            
                            #print "'%s' '%s'" % (key, value)
                            
                            char = getch(key)
                            if char is not None:
                                coding = sqp_models.Coding(question=question, 
                                                           characteristic=char,
                                                           choice = value,
                                                           user = user)
                                total_chars += 1
                                coding.save()
                        
                        if source_row_dict:
                            for key in chars_from_source.keys():
                                if chars_from_source[key] == None and key in source_row_dict.keys():
                                    char = getch(key)
                                    value = source_row_dict[key]
                                    
                                    #skip Not applicable codes
                                    #Diana's file uses . and ,
                                    #Daniel's file uses NA
                                    if value in ['.', ',', 'NA']:
                                        chars_from_source.pop(key)
                                        continue
                                    
                                    coding = sqp_models.Coding(question=question, 
                                                               characteristic=char,
                                                               choice = value,
                                                               user = user)
                                    coding.save()
                                    total_chars += 1
                                    chars_from_source[key] = value
                                else:
                                    chars_from_source.pop(key)
                                    
                        else:
                            chars_from_source = {}
                        
                        completeness = question.get_completeness(user, char_set)
                        if completeness == 'completely-coded':
                            question.set_completion(user=user, charset=char_set, complete=True, authorized=True)
                            COMPLETE += 1
                            is_complete = "COMPLETE" 
                        else:
                            question.set_completion(user=user, charset=char_set, complete=False, authorized=True)
                            INCOMPLETE += 1
                            is_complete = "NOT COMPLETE"
                            
                            last_branch = None
                            for branch in question.iter_branches(user=user, charset=char_set):
                                if branch:
                                    #print branch.label.characteristic
                                    last_branch = branch
                            
                            if last_branch:    
                                from_characteristic = last_branch.label.characteristic
                                branch = next_branch(from_characteristic, user, question, char_set)
                                if branch is not None:
                                    ##The next characteristic to code is the branch to_characteristic
                                    missing_char = branch.to_characteristic.short_name
                            else:
                                missing_char = 'domain'
                            
                        print '%s  %s First Missing:  %s' % (question, is_complete, missing_char)
                       
                        
                except Exception as e:
                    error = "MISSED '%s' '%s' '%s' '%s' '%s' Exception %s" % \
                    (row_study, row_country, row_language, row_item_name, row_dict['coder'], e)
                    print error
                    missed_rows.append(error)
                    exception = "%s" % e
                   
                vals = [question_id, row_country, row_language, row_study, row_item_name, 
                        found_db, found_diana, MTMM_Status, is_complete, 
                        source_question_id, str(chars_from_source), str(total_chars),  missing_char, exception] 
                
                log_file.write("\t".join(vals))
                log_file.write("\n") 
                
            joinfile.close()
            log_file.close()
            
            for row in missed_rows:
                print row
            
         
            
        #Import Source
        run_import(eng_only=True)
        #Import others
        run_import(eng_only=False)
        
        
        
        print "**************************************************************"
        
        
            
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
            'rfa_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'val': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'val_hi': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'val_lo': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
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
