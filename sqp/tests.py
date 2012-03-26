# -*- coding: utf-8 -*-

import unittest

from sqp import models, views_ui_functions
from django.contrib.auth.models import User
from django.conf import settings
import json
import types
from sqp import views_ui_exceptions 

#A collection of questions in various languages
test_languages = [
                     {'language_iso'        : 'eng',
                      'country_iso'         : 'GB',
                      'introduction_text'   : 'This is a question about bikes. Bikes have two wheels.',
                      'rfa_text'            : 'Please use the scale to select how much you like to ride your bike.',
                      'answer_text'         : 'I love to ride my bike\nI would rather drive my car\n I do not like bikes.'
                      },
                     {'language_iso'        : 'spa',
                      'country_iso'         : 'ES',
                      'introduction_text'   : u'Se trata de castañas. Las castañas son sabrosos.',
                      'rfa_text'            : u'Por favor, dime cómo te gustan castañas asadas.',
                      'answer_text'         : u'Me encantan las castañas\nOdio las castañas\nNo se preocupan por las castañas.'
                      },
                      {'language_iso'       : 'cat',
                      'country_iso'         : 'ES',
                      'introduction_text'   : u'Aquesta és una pregunta sobre les bicicletes. Motos tenen dues rodes.',
                      'rfa_text'            : u"Si us plau, utilitzeu l'escala per seleccionar quant t'agrada anar en bicicleta.",
                      'answer_text'         : u"M'agrada muntar la meva bicicleta\nPrefereixo conduir el meu cotxe\nNo m'agraden les motos"
                      },
                      {'language_iso'       : 'ell',
                      'country_iso'         : 'GR',
                      'introduction_text'   : u'Αυτή είναι μια ερώτηση για ποδήλατα. Τα ποδήλατα έχουν δύο τροχούς.',
                      'rfa_text'            : u'Παρακαλούμε χρησιμοποιήστε την κλίμακα για να επιλέξετε πόσο σας αρέσει να οδηγούν το ποδήλατό σας.',
                      'answer_text'         : u'Μου αρέσει να το ποδήλατο μου\nΘα ήθελα να οδηγείτε το αυτοκίνητό μου και όχι\n Δεν μου αρέσει ποδήλατα'
                      },
                     {'language_iso'        : 'rus',
                      'country_iso'         : 'RU',
                      'introduction_text'   : u'Это вопрос о велосипедах. Велосипеды имеют два колеса.',
                      'rfa_text'            : u'Пожалуйста, используйте масштаб, чтобы выбрать, сколько вы хотели бы ездить на велосипеде.',
                      'answer_text'         : u'Я люблю кататься на велосипеде\nЯ предпочел бы водить свой автомобиль\nЯ не люблю велосипеды'
                      },
                     {'language_iso'        : 'ekk',
                      'country_iso'         : 'EE',
                      'introduction_text'   : u'See on küsimus jalgratast. Bikes on kaks ratast.',
                      'rfa_text'            : u'Palun kasutage skaalal valida, kui palju sulle meeldib sõita oma jalgrattaga.',
                      'answer_text'         : u'Ma armastan sõita minu bike\nMa pigem saan oma autoga sõita\nMulle ei meeldi jalgratast'
                      },
                     {'language_iso'        : 'nld',
                      'country_iso'         : 'NL',
                      'introduction_text'   : u'Dit is een vraag over fietsen. Fietsen hebben twee wielen.',
                      'rfa_text'            : u'Gebruik de schaal aan te geven hoe veel u wilt uw fiets.',
                      'answer_text'         : u'Ik hou van mijn fiets te rijden\nIk zou liever mijn auto rijden\nIk houd niet van fietsen'
                      },
                      {'language_iso'       : 'fra',
                      'country_iso'         : 'FR',
                      'introduction_text'   : u"C'est une question sur les vélos. Roues ont deux roues.",
                      'rfa_text'            : u"S'il vous plaît utiliser l'échelle pour choisir combien vous voulez monter sur votre vélo.",
                      'answer_text'         : u"J'aime mon vélo\nJe préfère conduire ma voiture\nJe n'aime pas les vélos"
                      },
                      {'language_iso'       : 'por',
                      'country_iso'         : 'PT',
                      'introduction_text'   : u"Esta é uma pergunta sobre motos. Bicicletas têm duas rodas.",
                      'rfa_text'            : u"Por favor, use a escala para escolher o quanto você gosta de andar de bicicleta.",
                      'answer_text'         : u"Gosto de andar de bicicleta\nEu prefiro conduzir o meu carro\nEu não gosto de bicicletas."
                      },
                      {'language_iso'       : 'ita',
                      'country_iso'         : 'IT',
                      'introduction_text'   : u"Questa è una domanda su biciclette. Biciclette hanno due ruote.",
                      'rfa_text'            : u"Si prega di utilizzare la scala di selezionare quanto ti piace andare in bicicletta.",
                      'answer_text'         : u"Io amo andare in bicicletta\nPreferirei guidare la mia auto\nNon mi piacciono le biciclette."
                      },
                      {'language_iso'       : 'deu',
                      'country_iso'         : 'DE',
                      'introduction_text'   : u"Dies ist eine Frage über Fahrräder. Zweiräder haben zwei Rädern.",
                      'rfa_text'            : u"Bitte benutzen Sie den Maßstab zu wählen, wie viel Sie Ihr Fahrrad fahren wollen.",
                      'answer_text'         : u"Ich liebe es, mein Fahrrad\nIch würde lieber mein Auto\nIch mag keine Fahrräder"
                      },
                      {'language_iso'       : 'bul',
                      'country_iso'         : 'BG',
                      'introduction_text'   : u"Това е въпрос за колелета. Моторът има две колела.",
                      'rfa_text'            : u"Моля, използвайте скалата за да изберете колко често искате да дойде под наем.",
                      'answer_text'         : u"Обичам да карам моя мотор\nБих предпочел да карам колата си\nАз не обичам мотори"
                      },
                      {'language_iso'       : 'glg',
                      'country_iso'         : 'ES',
                      'introduction_text'   : u"Esta é unha pregunta sobre motos. Bicicletas teñen dúas rodas",
                      'rfa_text'            : u"Por favor, use a escala para escoller o que lle gusta andar en bicicleta.",
                      'answer_text'         : u"Gusto de andar en bicicleta\nEu preferiría meu coche\nEu non me gusta de motos"
                      }
                     ]



class NewUserTestCase(unittest.TestCase):
    
    def test_1_create_user(self):
        User.objects.create_user('john_test', 'lennon@thebeatles.com', 'johnpassword')

    def test_2_profile_correct(self):
        john    = User.objects.get(username='john_test')
        self.user = john
        profile = john.get_profile()
        self.assertEqual(profile.user, john) 
        self.assertEqual(profile.default_characteristic_set_id, settings.AUTH_PROFILE_DEFAULT_CHARACTERISTIC_SET_ID)
        
        #Add john to the English coders for convenience
        eng = models.Language.objects.get(iso='eng')
        eng.coders.add(john)
        eng.save()
        
 
#Test that the New Study function in the UI works correctly        
class UIStudyTestCase(unittest.TestCase):
    
    user     = None
 
    def setUp(self):
        self.user         = User.objects.get(username='john_test')
     
    def test_1_create_study(self):
        obj_request_body  = {'name' : 'My Test Study'}
        obj_response_body = views_ui_functions.create_or_update_study(self.user, obj_request_body)[0]
        self.study_id     = obj_response_body['id']
        self.assertEqual(type(self.study_id), types.LongType)
        
    def test_2_update_study(self):
        study_id = models.Study.objects.get(name = 'My Test Study').id 
         
        obj_request_body  = {'name' : 'My Test Study, Renamed'}
        obj_response_body = views_ui_functions.create_or_update_study(self.user, 
                                                     obj_request_body, studyId = study_id)[0]
        self.assertEqual(obj_response_body['name'], 'My Test Study, Renamed')
        
  
    def test_3_get_study(self):
        study_id = models.Study.objects.get(name = 'My Test Study, Renamed').id 
        
        obj_response_body = views_ui_functions.get_study(self.user, 
                                                         studyId = study_id)[0]
        self.assertEqual(obj_response_body['name'], 'My Test Study, Renamed')
        
      
class UIQuestionTestCase(unittest.TestCase):
    
    user         = None
    study        = None
    
    def setUp(self):
        self.user = User.objects.get(username='john_test')
        self.study = models.Study.objects.get(name="My Test Study, Renamed")  
    
    #Test that it is possible to create a question with a new item
    def test_1_create_question_new_item(self):
        obj_request_body  = {'studyId'          : self.study.id,
                             'itemCode'         : 'A4', 
                             'itemName'         : 'ABCDEF',
                             'itemDescription'  : 'This is a good question for testing',
                             'introText'        : 'My Test Question Intro',
                             'languageIso'      : 'eng',
                             'countryIso'       : 'AU',
                             'requestForAnswerText' : 'Please o please answer me!',
                             "answerOptionsTexts"   : ['Category One', 'Category Two']}
        
        obj_response_body = views_ui_functions.create_or_update_question(self.user, obj_request_body)[0]
        
        if not obj_response_body['id']:
            raise Exception('No id returned')
            
    
    #Test that it is possible to create a question with an existingitem
    def test_2_create_question_existing_item(self):
        obj_request_body  = {'studyId'          : self.study.id,
                             'itemCode'         : 'A4', 
                             'itemName'         : 'ABCDEF',
                             'itemDescription'  : 'Ist und bon veston testin',
                             'introText'        : 'Das is oto intro',
                             'languageIso'      : 'deu',
                             'countryIso'       : 'DE',
                             'requestForAnswerText' : 'reponze!',
                             "answerOptionsTexts"   : ['Category One', 'Category Two']}
        
        obj_response_body = views_ui_functions.create_or_update_question(self.user, obj_request_body)[0]
        new_question_id     = obj_response_body['id']
        self.assertEqual(type(new_question_id), types.LongType)
        question_new = models.Question.objects.get(id=new_question_id)
        question_existing = models.Question.objects.get(introduction_text = 'My Test Question Intro')
        self.assertEqual(question_new.item.id, question_existing.item.id)
        
    def test_3_update_question(self):
        obj_request_body  = {'studyId'          : self.study.id,
                             'itemCode'         : 'A4', 
                             'itemName'         : 'ABCDEF', 
                             'itemDescription'  : 'This is a good question for testing',
                             'introText'        : 'My Modified Test Question Intro',
                             'languageIso'      : 'eng',
                             'countryIso'       : 'AU',
                             'requestForAnswerText' : 'Please o please answer me!',
                             "answerOptionsTexts"   : ['Category One', 'Category Two']}
        
        question_id = models.Question.objects.get(introduction_text = 'My Test Question Intro').id

        
        obj_response_body = views_ui_functions.create_or_update_question(self.user, 
                                                     obj_request_body, questionId = question_id)[0]
                                                     
        self.assertEqual(obj_response_body['introText'], 'My Modified Test Question Intro')
        
    def test_4_get_question(self):
        question_id = models.Question.objects.get(introduction_text = 'My Modified Test Question Intro').id
        
        obj_response_body = views_ui_functions.get_question(self.user, 
                                                         questionId = question_id)[0]
        self.assertEqual(obj_response_body['introText'], 'My Modified Test Question Intro')


class UISuggestionTestCase(unittest.TestCase):
    """This requires tree tagger to be installed on the machine and confiured properly for each lanaguage
    """
    user         = None
    study        = None
    item         = None
    
    def setUp(self):
        self.user  = User.objects.get(username='john_test')
        self.study = models.Study.objects.get(name="My Test Study, Renamed")  
        self.item  = models.Item(study=self.study, admin='Z9',name="Q_Z9") 
        self.item.save()
    
    #Test that it is possible to create a question with a new item
    def test_nouns(self):
        
       
        
        for test_language in test_languages:
        
            language = models.Language.objects.get(iso=test_language['language_iso'])
            country  = models.Country.objects.get(iso=test_language['country_iso'])
            
            q = models.Question(item      = self.item,
                                language  = language,
                                country   = country,
                                introduction_text   = test_language['introduction_text'],
                                rfa_text            = test_language['rfa_text'],
                                answer_text         = test_language['answer_text']
                                )
            q.save()
            
            for char in['nnouns_quest', 'nnouns_ans']:
                try: 
                    characteristic = models.Characteristic.objects.get(short_name=char)
                    suggestion = models.CodingSuggestion.objects.get(question=q, characteristic=characteristic)
                    if(suggestion.value == 0):
                        raise self.failureException('suggestion was incorrect (0) for char %s in language %s' % (char, test_language['language_iso']))
                except models.CodingSuggestion.DoesNotExist:
                    raise self.failureException('No suggestion created for char %s in language %s' % (char, test_language['language_iso']))
           
            print "Language ok: %s" % test_language['language_iso']      
 
class QuestionPermissionTestCase(unittest.TestCase):
    """Test the question permissions work correctly for question.can_edit_details, 
       question.can_edit_text, and question.can_delete
    """
    user         = None
    other_user   = None
    study        = None
    item         = None
    country      = None
    language     = None
    question     = None
    
    def setUp(self):
        
        try:
            self.user = User.objects.get(username='john_test')
        except:
            self.user = User.objects.create_user('john_test', 'john@lennon.com', 'johnpassword')
            
        try:
            self.other_user  = User.objects.get(username='joan_test')
        except:
            self.other_user = User.objects.create_user('joan_test', 'joan@baez.com', 'joanpassword')
            
            
        self.study = models.Study.objects.get(name="My Test Study, Renamed")
        self.item = models.Item.objects.get_or_create(study=self.study, admin='Z2',name="Q_Z2")[0] 
        self.language = models.Language.objects.get(iso='eng')
        self.country  = models.Country.objects.get(iso='GB')
        
        
        self.question =  models.Question.objects.get_or_create(item      = self.item,
                            language  = self.language,
                            country   = self.country,
                            introduction_text   = u'Delete my',
                            rfa_text            = u'Please answer!!',
                            answer_text         = u'',
                            )[0]
        
        self.question.save()
        
        try:
            #Delete any existing relation so that we always start with a clean one
            user_question_relation = models.UserQuestion.objects.get(user=self.user, question=self.question)
            user_question_relation.delete()
        except:
            pass
    
    
    def test_delete_question(self):
        """Test question delete permissions"""
        self.question.created_by = self.other_user
        self.question.save()
        
        if self.question.can_delete(self.user):
            raise self.failureException('Question delete permission granted even though the user did not have permission')
       
        self.question.created_by = self.user
        self.question.save()
        if not self.question.can_delete(self.user):
            raise self.failureException('Permission to delete question denied for created_by')
        
    def test_edit_question_text(self):
        """Test edit text permission"""
        
        
        
        user_question_relation = models.UserQuestion.objects.create(user=self.user, question=self.question)
        user_question_relation.save()
        
        
        self.question.created_by = self.other_user
        self.question.save()
        
        if self.question.can_edit_text(self.user):
            raise self.failureException('Permission to edit text granted when not expected')
        
        user_question_relation.can_edit_text = True
        user_question_relation.save()
        
        if not self.question.can_edit_text(self.user):
            raise self.failureException('Permission to edit text not granted')
        
        user_question_relation.delete()
        
        self.question.created_by = self.user
        self.question.save()
        if not self.question.can_edit_text(self.user):
            raise self.failureException('Permission to edit question text denied for created_by')
        
 
 
class CompletionTestCase(unittest.TestCase):
    """Test that the completion table is being updated correctly when a code is saved
    """
    user         = None
    profile      = None
    question     = None
    domain_char  = None
    charset      = None
    
    def setUp(self):
        self.user         = User.objects.get(username='john_test')
        self.profile      = self.user.get_profile()
        self.question     = models.Question.objects.get(introduction_text='This is a question about bikes. Bikes have two wheels.')
        self.domain_char  = models.Characteristic.objects.get(short_name = 'domain')
        self.charset      = self.profile.default_characteristic_set_id

    def test_1_ui_completion_is_set_out_of_date(self):
        
        #First test that a new competion record marked as out_of_date gets created
        obj_request_body = {'choice' : 0, 'secondsTaken' : 2}
        views_ui_functions.update_coding(self.user, obj_request_body, self.question.id, self.domain_char.id)
        try:
            completion = models.Completion.objects.get(user=self.user, question=self.question, characteristic_set = self.charset)
            if completion.out_of_date != True:
                raise self.failureException('Completion created is not marked as out of date (out_of_date != True)')
        except:
            raise self.failureException('No initial out of date completion record created')
        
        #Make sure exisiting completion records are also invalidated
        #set the completion object to not out of date
        completion.out_of_date = False
        completion.save() 
        
        obj_request_body = {'choice' : 1, 'secondsTaken' : 2}
        views_ui_functions.update_coding(self.user, obj_request_body, self.question.id, self.domain_char.id)

        completion = models.Completion.objects.get(user=self.user, question=self.question, characteristic_set = self.charset)
        if completion.out_of_date != True:
            raise self.failureException('Existing completion is not marked as out of date after coding update (out_of_date != True)')
        
    def test_2_ui_question_list_updates_completion(self):
        #Getting the question list should first update any records with out_of_date completion records
        views_ui_functions.get_question_list(user=self.user)
        try:
            models.Completion.objects.get(user=self.user, characteristic_set = self.charset, out_of_date=True)
            raise self.failureException('Not all corresponding out_of_date completion records were updated when loading the question list')
        except:
            #there should be no records so here we just pass
            pass
        
    def test_3_ui_get_coding_updates_completion(self):
        #Getting the next coding should mark the question as not complete, but up to date
        
        #Set up the completion object to make it look like the question is complete
        completion = models.Completion.objects.get(user=self.user, question=self.question, characteristic_set = self.charset)
        completion.out_of_date = True
        completion.complete = True
        completion.save()
        
        views_ui_functions.get_coding(user=self.user, questionId=self.question.id)
        try:
            models.Completion.objects.get(user=self.user, question=self.question, characteristic_set=self.charset, out_of_date=True)
            raise self.failureException('out_of_date completion record was updated when getting the next coding for a question')
        except:
            #there should be no records so here we just pass
            pass
        
#Test that the New Study function in the UI works correctly        
class UIDeleteStudyTestCase(unittest.TestCase):
    user     = None
    study_id = None
    
    def setUp(self):
        self.user       = User.objects.get(username='john_test')
        self.study_id   = models.Study.objects.get(name='My Test Study, Renamed').id
        
    def test_delete_study(self):
        obj_response_body = views_ui_functions.delete_study(self.user, studyId = self.study_id)[0]
        self.assertEqual(obj_response_body['name'], 'My Test Study, Renamed')     
  
#Delete the user and any other clean up objects
class DeleteUserTestCase(unittest.TestCase):
    def test_delete_user(self):
        john    = User.objects.get(username='john_test')
        
        #Add john to the English coders for convenience
        eng = models.Language.objects.get(iso='eng')
        eng.coders.remove(john)
        eng.save()
        john.delete()  

   
#The tests must be added here, and then they will be run in order
test_order = (NewUserTestCase,
              UIStudyTestCase,
              UIQuestionTestCase,
              UISuggestionTestCase,
              QuestionPermissionTestCase,
              CompletionTestCase,
              UIDeleteStudyTestCase,
              DeleteUserTestCase)
     
        