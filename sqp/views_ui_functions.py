# -*- coding: utf-8 -*-

from sqp import models
from sqp import views_ui_model_views
from sqp.views_ui_utils import URL, get_branch, get_label, get_codes_list, get_predictor

from django.db import connection, transaction
import math
import textile
from subprocess import Popen
from django.conf import settings
if settings.DEBUG: import time
from django.db.models import Q
from sqp import views_ui_exceptions
from sqp.variable_labels import extra_variable_labels

import json
import sys



SUCCESS   = 1
FAILED    = 0


def pythify(name):
    return name.strip(' ').lower().replace(' ', '_')

def get_username(request_user, user):
    if request_user.is_staff:
        return user.username
    else:
        return "User %s" % user.id


def get_assigned_questions(user):
    """Returns a list of questions assigned to a user
    """
    characteristicSetId = user.profile.default_characteristic_set_id
    charset = models.CharacteristicSet.objects.get(id=characteristicSetId) 
    
    obj_response_body = []
    meta = {}
    for user_question in models.UserQuestion.objects.filter(user=user):
        question_model_view = views_ui_model_views.question_base(user_question.question)
        question_model_view['completeness'] = user_question.question.get_completeness(user,charset)
        obj_response_body.append(question_model_view)
    
    return obj_response_body, meta, SUCCESS

def render_predictions(user, questionId, \
                      predictionKeyList, completionId=0, characteristicSetId = False):
    """Loads a list of prediction objects and returns the html from the 
       prediction.view.render method.
       In addition it saves all the predictions to the completion table for re-use since
       the predictor object is memory intensive
    """

    if characteristicSetId is False:
        characteristicSetId = user.profile.default_characteristic_set_id
    
    
    
    charset = models.CharacteristicSet.objects.get(id=characteristicSetId) 
    question = models.Question.objects.get(pk=questionId)
   
    completionId = int(completionId)
    if completionId:
        completion = models.Completion.objects.get(pk=completionId)
        codes = question.get_codes(completion.user,charset)
    else:
        codes = question.get_codes(user,charset)
        completion = models.Completion.objects.get(user=user, question=question,
                characteristic_set=charset)

    if settings.DEBUG: start = time.time()


    try:
        #Here we check if the prediction was rendered
        completion.predictions['rendered']
        
        #Uncomment the next line to disable cache
        #completion.predictions['disable_display_of_cached_predictions']
        
        #And if there was any errors in the last render, then we want to render it again
        if completion.predictions['errors']['general_error'] != False \
          or len(completion.predictions['errors']) > 1:
            raise Exception()
        
    except :
        completion.predictions = {'rendered' : True, 'errors' : {'general_error' : False}}
        
        try:
            # Connect to the predictor through Pyro. The pyro name server is used to
            #find the predictor object.
            predictor = get_predictor() 
            
            predictions = predictor.get_predictions(question.country_prediction.iso, question.language.iso, get_codes_list(codes))        
            
            if settings.DEBUG: 
                elapsed = time.time() - start
                print "Got the predictions, took %2.4f s" % elapsed
         
            for prediction in models.Prediction.objects.all():
                try:
                    try:
                    # Look up the Prediction in the predictions dict
                        prediction_return = \
                            predictions[\
                            pythify(prediction.paramater.name)][pythify(prediction.view.name)]
                    except KeyError:
                        #If it is in the db but not the predictions
                        # object, just skip this Prediction
                        continue  
            
                    completion.predictions[prediction.key] = prediction_return
                    
                except Exception as e:
                    completion.predictions['errors'][prediction.key] =  "%s - %s" % (type(e), str(e))
                    print 'prediction %s failed with exception %s' % (prediction.key, e)
            
        except Exception as e:
            completion.predictions['errors']['general_error'] = str(e)

        completion.save()
        
    obj_response_body = {}
    
    if completion.predictions['errors']['general_error']:
        meta = {'general_error' : completion.predictions['errors']['general_error']}
        successful = FAILED
    else:
        for prediction_key in predictionKeyList.split(','):
            try:
                prediction = models.Prediction.objects.get(key=prediction_key)
                prediction_return = completion.predictions[prediction.key]
                obj_response_body[prediction_key] = prediction.view.render(prediction_return)
            except Exception as e:
                
                try:
                    error_info = completion.predictions['errors'][prediction.key]
                except:
                    error_info = "%s - %s" % (type(e), str(e))
                
                obj_response_body[prediction_key] = \
                    '<a title="Error - Click for info" class="hlinkclass" onclick="alert(this.childNodes[1].innerHTML)"> \
                    <span style="display:none">Error: %s</span>-99</a>' % error_info
                    
        meta = {}
        successful = SUCCESS
    
    return obj_response_body, meta, successful
    
def get_prediction_list(user):
    """
    Get a simple list of paramaters and views that could be shown in a prediction"""
    
    obj_response_body = []
    
    for prediction in models.Prediction.objects.all():
        
        param_view = {'predictionId'  : prediction.id,
                      'paramaterName' : prediction.paramater.name,
                      'viewName'      : prediction.view.name,
                                 }
        added = False
        for i in range(0, len(obj_response_body)):
            if obj_response_body[i]['paramaterName'] ==  prediction.paramater.name:
                obj_response_body[i]['paramaterViews'].append(param_view)
                added = True
        
        if not added:
            obj_response_body.append({'paramaterName' : prediction.paramater.name,
                                         'paramaterViews' : [param_view,]})
        
    return obj_response_body, {}, SUCCESS


def get_xnames(user):
    predictor = get_predictor()
    return json.dumps(predictor.get_xlevels(scale_basic='2'))

def get_potential_improvements(user, questionId, xname, params, completionId=0, characteristicSetId=False):
    """Returns all of the potential quality improvements for a coding set
    """
    
    question = models.Question.objects.get(pk=questionId)
    
    completionId = int(completionId)
    
    if completionId:
        completion = models.Completion.objects.get(pk=completionId)
        for_user = completion.user
    else:
        for_user = user
       
    if characteristicSetId is False:
        characteristicSetId = for_user.profile.default_characteristic_set_id
        
    charset = models.CharacteristicSet.objects.get(id=characteristicSetId) 
    codes = question.get_codes(for_user,charset)
      
    predictor = get_predictor()
            
    improvements = {}
    
    params = params.split(',')
    
    if 'choiceOptions' in params:
        loadChoiceOptions = True
        params.remove('choiceOptions')
    else:
        loadChoiceOptions = False
    

    for what in params:
        selected_improvements = predictor.get_conditional_effects(question.country.iso, question.language.iso, \
                                     get_codes_list(codes), what, xname)
        
        # for i in range(0, len(selected_improvements)):
        #     "Round any boolean keys"
        #     print type(selected_improvements[i][0])
        
        
        improvements[what] = selected_improvements
    
    #We take advantage of this ajax call to add on the choice options
    #if they were requested by the client
    if loadChoiceOptions:
        choice_options = []
        coding = None
        
        try:
            characteristic = models.Characteristic.objects.get(short_name=xname) 
            
            try:                              
                coding = models.Coding.objects.get(user=for_user, question=question, 
			characteristic=characteristic)
            except models.Coding.DoesNotExist:
                pass
            
            if  characteristic.widget.name == 'radiobuttons':
                for label in characteristic.label_set.all():
                   
                    choice_options.append({'labelName'      : label.name,
                                           'labelCode'      : label.code })
            #Check the extra labels
            if xname in extra_variable_labels:
                choice_options += extra_variable_labels[xname]
            
            improvements['variableName'] = characteristic.name
            improvements['variableDescription'] = textile.textile(characteristic.desc)
        except models.Characteristic.DoesNotExist:
            improvements['variableName'] = xname
            pass
        
        improvements['choiceOptions'] = choice_options
        if coding is not None:
            #Some chars are combined into one variable, so we try to accomodate that here
            #By setting the current value as the more specific choice
            
            if xname == 'concept' and coding.choice == '7':
                #Other concepts
                #We show the code for the vairable for the other simple concepts 70,71,72 etc...
                #These match up with codes in extra_variable_labels from variable_labels.py
                sub_char = models.Characteristic.objects.get(short_name='conc_simple')
                try:                              
                    sub_coding = models.Coding.objects.get(user=for_user, question=question, 
                                                       characteristic=sub_char)
                    improvements['currentValue'] = '7' + sub_coding.choice
                except models.Coding.DoesNotExist:
                    improvements['currentValue'] = '7' 
                    
            elif xname == 'domain' and coding.choice == '1':
                #Other concepts
                #We show the code for the vairable for the other simple concepts 70,71,72 etc...
                #These match up with codes in extra_variable_labels from variable_labels.py
                sub_char = models.Characteristic.objects.get(short_name='natpoldomain')
                try:                              
                    sub_coding = models.Coding.objects.get(user=for_user, question=question, 
                                                       characteristic=sub_char)
                    improvements['currentValue'] = '1' + sub_coding.choice
                except models.Coding.DoesNotExist:
                    improvements['currentValue'] = '1' 

                
            else: 
                improvements['currentValue'] = coding.choice
        else:
            improvements['currentValue'] = '__none__'
            
            
    
        
    return improvements, {}, SUCCESS


def get_characteristic_set_list(user):
    """
    Get a simple list of characteristic sets that have been assigned to the logged in user"""
    
    obj_response_body = []
    
    for characteristic in user.characteristicset_set.all():
        obj_response_body.append({'id'   : characteristic.id,
                                  'name' : characteristic.name})
    
    return obj_response_body, {}, SUCCESS



def item_autocomplete(user, studyId, term):
    """
    Auto complete for item type ahead suggest, 
    a study must be selected in order to suggest an item"""
    results = []
    
    if studyId != 'undefined':
        query_set = models.Item.objects.filter(name__icontains=term, study = models.Study.objects.get(pk=int(studyId)))
      
        for item in query_set.order_by('name')[0:10]:
                results.append({'id'          : item.id, 
                                'label'       : item.name, 
                                'value'       : item.name,
                                'description' : item.long_name,
                                'code'        : item.admin,
                                })
    
    #In views_ui_calls.py item_autocomplete is defined with the return type direct
    #so here we only return the results which are in a format friendly to the jQuery ui
    #autocomplete widget
    return json.dumps(results)

def item_can_edit(user, studyId, itemName):
    """
    A utility function that takes a studyId and an itemName.
    First an item lookup is attempted and the user's permission is checked
    If no item exists with that name for this study then we return true
    """
    can_edit = False
    
    try:
        study = models.Study.objects.get(pk=int(studyId))
        item = models.Item.objects.get(study=study, name=itemName)
        can_edit = item.can_edit(user)
    except models.Item.DoesNotExist:
        can_edit = True
   
    return json.dumps({'canEdit' : can_edit})

def get_study_list(user):
    """
    Return a list of studies that a user has been assigned to. This should be both global studies, and
    the users own studies"""

    obj_response_body = []
    
    #Show studies created by the user (created_by=user)
    #Show sutdies created in the admin (created_by=None)
    #Show studies created by other trusted users (created_by__profile__is_trusted=True)
    # User 211 is RECSM and 1121 is the demouser, both must be seen in studies list beside be not trusted
    if user.username == 'demouser':
        query = Q(created_by=user)
    else:
        query = Q(created_by=user) | Q(created_by=None) | Q(created_by__profile__is_trusted=True) | Q(created_by=211)
    
    for study in models.Study.objects.filter(query):
        
        obj_response_body.append({'id'      : study.id,
                                  'name'    : study.name,
                                  'canEdit' : study.created_by == user,
                                  'url'     : URL.study(study.id)})
                                  
    return obj_response_body, {}, SUCCESS

def get_study_list_fitted(user):
    """
    Return a list of studies that a user has been assigned to. This should be both global studies, and
    the users own studies"""

    obj_response_body = []

    #Show studies created by the user (created_by=user)
    #Show sutdies created in the admin (created_by=None)
    #Show studies created by other trusted users (created_by__profile__is_trusted=True)
    # User 1121 is the demouser, must be seen in study list in new question  beside be not trusted

    if user.username == 'demouser':
        query = Q(created_by=user)
    else:
        query = Q(created_by=user) | Q(created_by=None) | Q(created_by__profile__is_trusted=True)

    for study in models.Study.objects.filter(query):

        obj_response_body.append({'id'      : study.id,
                                  'name'    : study.name,
                                  'canEdit' : study.created_by == user,
                                  'url'     : URL.study(study.id)})

    return obj_response_body, {}, SUCCESS

def get_country_list(user):
    """
    Return a list of countries that a user has been assigned to.
    """

    obj_response_body = []
    
           
    for country in models.Country.objects.all():
        obj_response_body.append({'iso'   : country.iso,
                                  'name' : country.name})
    
    return obj_response_body, {}, SUCCESS

def get_country_prediction_list(user):
    """
    Return a list of countries that a user has been assigned to.
    """
    obj_response_body = []
           
    for country in models.Country.objects.all().filter(available=True):
        obj_response_body.append({'iso'   : country.iso,
                                  'name' : country.name})
    
    return obj_response_body, {}, SUCCESS


def get_language_list(user):
    """
    Return a list of languages that a user has been assigned to.
    """

    obj_response_body = []
   
    for language in models.Language.objects.all():
        obj_response_body.append({'iso'  : language.iso,
                                  'name' : language.name})
    
    return obj_response_body, {}, SUCCESS


def get_question(user, questionId, completionId=False, characteristicSetId = False, prepSuggestions=False):
    """
    Retrieve a Question object, annotating it with completion data from 
    the database and Related objects Item, Study, Language and Country."""
    
    if characteristicSetId is False:
        characteristicSetId = user.profile.default_characteristic_set_id
     
    charset = models.CharacteristicSet.objects.get(id=characteristicSetId) 
   
    question = models.Question.objects.get(id=questionId)
    
    if not question.can_access(user):
        raise views_ui_exceptions.ServiceError(views_ui_exceptions.no_permission, \
                                                    'Operation not permitted');

    #Prep the answer option text into an array
    if question.answer_text and question.answer_text.strip() != '':
        answer_options_text = question.answer_text.strip(' \t\n\r'). \
                                        replace('\r', '').split('\n')
    else:
        answer_options_text = []
        
    if prepSuggestions and models.CodingSuggestion.objects.filter(question=question).count() == 0:
        #generate suggestions which is done in Question.save()
        question.save()
    
    if completionId:        
        completion = models.Completion.objects.get(pk=completionId)
        completeness = question.get_completeness(completion.user, completion.characteristic_set)
    else:
        completeness = question.get_completeness(user, charset)
    
    #Set some defaults
    prediction_quality = 0
    prediction_quality_coefficient = 0
    prediction_validity_coefficient = 0
    prediction_reliability_coefficient = 0
    show_prediction = 0 #Falsy
    
    if completeness == 'completely-coded':
        
        try:
            var_list = 'question_quality,question_quality_coefficient,question_validity_coefficient,question_reliability_coefficient'
            qual = render_predictions(user, question.id, var_list, characteristicSetId=characteristicSetId)
            prediction_quality = qual[0]['question_quality']
            prediction_quality_coefficient = qual[0]['question_quality_coefficient']
            prediction_validity_coefficient = qual[0]['question_validity_coefficient']
            prediction_reliability_coefficient = qual[0]['question_reliability_coefficient']
            show_prediction = 1 #Truthy
        except:
            #The variables should stay at the defaults above
            pass

    if question.language.iso in ['arb', 'heb' ]:
        rtl = True
    else:
        rtl = False
    
    obj_response_body = {
            "id":                   question.id,
            "hasMTMM":              False,
            "url":                  URL.question(question.id),
            "urlCodingHistory":     URL.question_coding_history(question.id),
            "studyId":              question.item.study.id,
            "languageIso"  :        question.language.iso,
            "countryIso"  :         question.country.iso,
            "countryPredictionIso": question.country_prediction.iso,
            "studyName":            question.item.study.name,
            "itemPart":             question.item.main_or_supplementary(),
            "itemCode":             question.item.admin,
            "itemName" :            question.item.name, 
            "itemId  " :            question.item.id,   
            "country":              question.country.name,
            "countryPrediction":    question.country_prediction.name,
            "language":             question.language.name,
            "itemDescription":      question.item.long_name,
            "introText":            question.introduction_text,
            "requestForAnswerText": question.rfa_text,
            "answerOptionsTexts":   answer_options_text,
            "completeness":         completeness,
            "predictionQuality" :   prediction_quality,
            "predictionQualityCoefficient" : prediction_quality_coefficient,
            "predictionValidityCoefficient" : prediction_validity_coefficient,
            "predictionReliabilityCoefficient" : prediction_reliability_coefficient,
            "showPrediction":       show_prediction,
            "canEditText" :         question.can_edit_text(user),
            "canEditDetails" :      question.can_edit_details(user),
            "canEditItem" :         question.item.can_edit(user),
            "rtl"         :         rtl
             }

    if question.rel:
        obj_response_body['hasMTMM'] = True
        MTMM = {}


        MTMM['MTMM_rel']      = question.rel
        MTMM['MTMM_relLo']   = question.rel_lo
        MTMM['MTMM_relHi']   = question.rel_hi
        MTMM['MTMM_val']      = question.val
        MTMM['MTMM_valLo']   = question.val_lo
        MTMM['MTMM_valHi']   = question.val_hi
        MTMM['MTMM_qual']     = question.rel * question.val

        if question.rel_lo and question.val_lo:
            MTMM['MTMM_qualLo']  = question.rel_lo * question.val_lo
            MTMM['MTMM_qual2Lo'] = MTMM['MTMM_qualLo'] * MTMM['MTMM_qualLo']
        if question.rel_hi and question.val_hi:
            MTMM['MTMM_qualHi']  = question.rel_hi * question.val_hi
            MTMM['MTMM_qual2Hi'] = MTMM['MTMM_qualHi'] * MTMM['MTMM_qualHi']

        if question.rel: MTMM['MTMM_rel2']     = question.rel * question.rel
        if question.rel_lo: MTMM['MTMM_rel2Lo']  = question.rel_lo * question.rel_lo
        if question.rel_hi: MTMM['MTMM_rel2Hi']  = question.rel_hi * question.rel_hi
        if question.val: MTMM['MTMM_val2']     = question.val * question.val
        if question.val_lo: MTMM['MTMM_val2Lo']  = question.val_lo * question.val_lo
        if question.val_hi: MTMM['MTMM_val2Hi']  = question.val_hi * question.val_hi
        if question.rel and question.val: MTMM['MTMM_qual2']    = (question.rel * question.val) * (question.rel * question.val)


        for key in MTMM:
            MTMM[key] = str(MTMM[key])[0:5]


        obj_response_body = dict(MTMM.items() + obj_response_body.items())

    other_predictions = []
    user_prediction_is_authorized = False
    
    for completion in models.Completion.objects.filter(question=question, complete=True, characteristic_set=charset, authorized=False):
        if completion.user != user:
            qual = render_predictions(user, question.id, 'question_quality', completion.id, characteristicSetId)
            try:
                question_quality = qual[0]['question_quality']
            except:
                question_quality = -99
                
            other_predictions.append({ 'questionId' : question.id,
                                       'user' :  get_username(user, completion.user),
                                       'predictionQuality'  : question_quality,
                                       'completionId' : completion.id,
                                       'isAuthorized' : 0
                                    })
        
            
    
    try:
        #TODO:Change the below line to use get, not filter as only one coding should exist
        #Also, put constraint on database
        completion = models.Completion.objects.get(question=question, complete=True, characteristic_set=charset, authorized=True)
        qual = render_predictions(user, question.id, 'question_quality', completion.id,characteristicSetId)
       
        try:
            question_quality = qual[0]['question_quality']
        except:
            question_quality = -99
            
        obj_response_body['authorizedPrediction'] = {'questionId' : question.id,
                                                     'user' : get_username(user, completion.user),
                                                     'predictionQuality'  : question_quality,
                                                     'completionId' : completion.id,
                                                     'isAuthorized' : 1
                                                     }
        has_authorized_prediction = True
        
        if completion.user == user:
            user_prediction_is_authorized = True
            
    except models.Completion.DoesNotExist:
        has_authorized_prediction = False
        
    obj_response_body['otherPredictions'] = other_predictions
    obj_response_body['hasAuthorizedPrediction'] = has_authorized_prediction
    obj_response_body['hasOtherPredictions'] = len(other_predictions) > 0
    obj_response_body['ownPredictionIsAuthorized'] = user_prediction_is_authorized
    obj_response_body['otherCountryPrediction']= (question.country != question.country_prediction)

    return obj_response_body, {}, SUCCESS

def delete_question(user, questionId):
    """
    Delete a question owned by a user. This should delete all associated codings for the question. """
    question = models.Question.objects.get(pk=questionId)
    
    if question.can_delete(user):
        obj_response_body, meta = get_question(user, questionId) 
        question.delete()
        return obj_response_body, meta, SUCCESS
    else:
        raise views_ui_exceptions.ServiceError(views_ui_exceptions.no_permission, \
                                                    'Operation not permitted');
    
def create_or_update_question(user, obj_request_body, questionId = False):
  
    """Create or update a question. If there is no question id, a new record will be created. """
    if not questionId:
        #If there is no question id, we create a new question
        question = models.Question()
        previous_item_code = None
        question.created_by = user
    else:
        question = models.Question.objects.get(pk=questionId)
        previous_item_code  = question.item.admin
        previous_item_study = question.item.study 
        
    #Do some permission checking on the save event    
    if not question.can_edit_text(user):
        raise views_ui_exceptions.ServiceError(views_ui_exceptions.no_permission, \
                                                    'Operation not permitted');
    
    #Update the properties related to the text of the question
    question.rfa_text = obj_request_body['requestForAnswerText']
    question.introduction_text = obj_request_body['introText']
    question.answer_text = "\n".join(obj_request_body["answerOptionsTexts"])
    
    if question.can_edit_details(user):
        
        item_code = obj_request_body.get('itemCode')
        item_name = obj_request_body['itemName']
        item_description = obj_request_body['itemDescription']
        study_id  = int(obj_request_body.get('studyId'))
        study = models.Study.objects.get(pk=study_id)
        
        def get_long_name():
            if item_description :
                q_text = item_description
            else:
                if obj_request_body['introText']:
                    q_text = obj_request_body['introText'][0:60] 
                else:
                    q_text = obj_request_body['requestForAnswerText'][0:60]
                    
            return q_text
        
        try:
            #Try to find an exact match
            item = models.Item.objects.get(study     = study,
                                           admin     = item_code,
                                           name      = item_name)
            
            question.item = item
           
            if item.can_edit(user):
                item.long_name = get_long_name()
                item.admin     = item_code
                item.save()
            elif item.long_name != item_description or item.admin != item_code:
                raise views_ui_exceptions.ServiceError(views_ui_exceptions.no_permission, \
                                                    'Since this item is shared, you may not edit the description or the code.');
            
        except models.Item.DoesNotExist:
            #But if there is no matching existing item by name and study, we create one
            new_item = models.Item(admin        = item_code,
                               study        = study,
                               long_name    = get_long_name(),
                               name         = item_name,
                               created_by   = user)
            new_item.save()
         
            try:
                old_item = question.item 
               
                #Check to see if the old item is orphaned
                if old_item is not None       \
                    and old_item.created_by == user        \
                    and models.Question.objects.filter(item=old_item).count() <= 1:
                    
                    #No questions exist for this item so we delete it
                    old_item.delete()           
            except:
                pass
                
            question.item = new_item
                
        
        country = models.Country.objects.get(iso=obj_request_body['countryIso'])
        country_prediction = models.Country.objects.get(iso=obj_request_body['countryPredictionIso'])
        language = models.Language.objects.get(iso=obj_request_body['languageIso'])
        
        question.country = country
        question.country_prediction = country_prediction
        question.language = language
        
    
    question.save()
    
    return get_question(user, questionId=question.id)
    

def get_next_question(user, fromQuestionId, countryIso=False, languageIso=False, 
                      studyId=False):
    
    questions = get_question_list(user, countryIso=countryIso, 
                                        languageIso=languageIso,
                                        studyId=studyId, 
                                        completeness=2, #To be coded
                                        returnFormat = 'id_list',
                                        fromQuestionId = fromQuestionId);
    
    
    fromQuestionId = int(fromQuestionId)
     
    #We try to return the next question 
    #from the question we were at, or if no
    #ids are after the from_q_id we return the
    #first other id we find                                  
    next_q_id = None
    from_q_found = False                                    
    for id in questions:
        if from_q_found:
            next_q_id = id
            break
        if id == fromQuestionId:
            from_q_found = True
        
        #Default to the first id we find
        #this will be used in case there is
        #no id after the from question id 
        #but there are other non coded questions        
        if id != fromQuestionId and not next_q_id:
            next_q_id = id
          
    if next_q_id is not None:
        return get_question(user, questionId=next_q_id)
    else:
        return {}, {}, SUCCESS
    

def get_question_list(user, countryIso=False, languageIso=False, studyId=False, \
                      characteristicSetId = False, completeness=0, MTMM=0, page=1, recordsPerPage=20, 
                      returnFormat='full_list', q="", fromQuestionId=None):
    """
    Get a list of questions for a user with completeness based on a characteristic set. 
    The list contains a summary of country, language, item, and study
    completeness 0 = All Questions
    completeness 1 = Complete Questions
    completeness 2 = Todo Questions
    completeness 3 = With predictions made by any user
    
    q is for query, like in google search
    
    """
    
    completeness = int(completeness)
    MTMM = int(MTMM)
    
    if characteristicSetId is False:
      
        characteristicSetId = user.profile.default_characteristic_set_id
        
    obj_response_body          = []
    
    query_params = ["1"]
    
    charset = models.CharacteristicSet.objects.get(id=characteristicSetId) 
    
    #Check for questions by this user that have completeness records that are out of date
    #For any out of date records we update the completeness here
    out_of_date_completions = models.Completion.objects.filter(out_of_date=True, characteristic_set=charset)
    for out_of_date_item in out_of_date_completions:
        out_of_date_item.question.update_completion(user=out_of_date_item.user, for_charset=charset)
   
    if countryIso:
        query_params.append("q.country_id = '%s'" % models.Country.objects.get(iso=countryIso).iso) 
    if languageIso:
        query_params.append("q.language_id = %s" % models.Language.objects.get(iso=languageIso).id)
    if studyId:
        items = []
        study_item_set = models.Study.objects.get(id=studyId).item_set.all()
        
        if len(study_item_set):
            for i in study_item_set:
                items.append(str(i.id))
            query_params.append("q.item_id IN (%s)" % ','.join(items))
        else:
            #We force an empty result set since there are no items
            query_params.append("0")
            
    restrict_complete_by_user = 'AND c.user_id = %s' % int(user.id)
    if completeness == 1:
        query_params.append('c.complete = 1' )
    elif completeness == 2:
        query_params.append('c.complete != 1')
    elif completeness == 3:
        query_params.append('c.complete = 1' )
        restrict_complete_by_user = ''
    
    if MTMM == 1:
        query_params.append('q.rel IS NOT NULL')    
    
    #Pagination meta info
    page = int(page)
    recordsPerPage = int(recordsPerPage)
    start_record = (page -1) * recordsPerPage

    #We only show trusted userprofile questions, created questions, or assigned questions
    """user_assigned_questions = [str(int(uq.question_id)) for uq in models.UserQuestion.objects.filter(user=user)]
    if len(user_assigned_questions) > 0:
        user_assigned_query = 'OR q.id IN (' +  ','.join(user_assigned_questions) + ')'
    else:
        user_assigned_query = ''
        
    #Questions created through the admin or by trusted users
    trusted_user_query = 'OR (q.created_by_id IS NULL) OR (up.is_trusted = 1)'   
     
    query_params.append('(q.created_by_id = %s %s %s)' % (user.id, user_assigned_query, trusted_user_query))
    """

    if q != '':
        q =  '%' + q + '%'
        query = "(q.introduction_text LIKE %s OR q.rfa_text LIKE %s OR q.answer_text LIKE %s OR i.name LIKE %s OR i.long_name LIKE %s OR i.admin LIKE %s)" 
        query_params.append(query)
    
    
    where = 'WHERE (' + '\n AND '.join(query_params) + ')'
       
        
    #Used to find the next question in the list for coders that need to code the next question
    if fromQuestionId is not None:
        where += 'OR (q.id = %s)' % int(fromQuestionId)
        
    base_sql = """
    FROM sqp_question as q
    LEFT JOIN sqp_item as i ON i.id = q.item_id
    LEFT JOIN sqp_userprofile AS up ON q.created_by_id = up.user_id
    LEFT OUTER JOIN sqp_completion as c ON q.id = c.question_id
         AND c.characteristic_set_id = %s
         %s
     %s
    ORDER BY i.study_id, q.country_id, q.language_id, i.admin_letter, i.admin_number, q.id
    """ % (int(characteristicSetId), restrict_complete_by_user,  where)
    
    if returnFormat == 'id_list':
        
        "for the get next question query we return a complete list of ids"
        sql = "SELECT q.id" + base_sql
        
        cursor = connection.cursor()
        if q != '':
            cursor.execute(sql, [q,q,q,q,q,q])
        else:
            cursor.execute(sql)
        
        id_list = []
        for row in cursor.fetchall():
            id_list.append(int(row[0]))
            
        return id_list
        
    else:
        
        sql = "SELECT q.*, c.complete" + base_sql + 'LIMIT %s, %s' % (start_record, recordsPerPage)
        
        
        if q != '':
            qs = models.Question.objects.raw(sql, [q,q,q,q,q,q])
        else:
            qs = models.Question.objects.raw(sql)
            
        for question in qs:
            
            
            #Use a quicker lookup for completeness
            #question.complete exists as a property because it was included in the sql above
            if question.complete:
                complete = 'completely-coded'
            else:
                ncodings = models.Coding.objects.filter(question = question, user = user).count()
                if ncodings > 0:
                    complete = 'partially-coded'
                else:
                    complete = 'not-coded'
                    
            
            has_authorized_prediction = False
            has_own_prediction = False
            
            total_other_predictions = 0
            for completion in models.Completion.objects.filter(complete=True,characteristic_set=charset, question=question):
                
                if completion.authorized:
                    has_authorized_prediction = True
                
                if not completion.authorized and completion.user != user:
                    total_other_predictions += 1 
                
                if completion.user == user:
                    has_own_prediction = True
            
            question_model_view = views_ui_model_views.question_base(question)
            
            question_model_view = dict(question_model_view.items() + {
                
                "completeness"            :     complete,  #This refers to the user's own coding of the question
                "hasAuthorizedPrediction" :     has_authorized_prediction,
                "hasOwnPrediction"        :     has_own_prediction,
                "totalOtherPredictions"   :     total_other_predictions
                }.items())
            
            obj_response_body.append(question_model_view)
        
        
        
        #Build up the meta for pagination
        #First we get the total records
        cursor = connection.cursor()
        # Data retrieval operation - no commit required
        sql = "SELECT COUNT(q.id) " + base_sql
        if q != '':
            cursor.execute(sql, [q,q,q,q,q,q])
        else:
            cursor.execute(sql)


        row = cursor.fetchone()    
        total_records = int(row[0])
        #Then do a bit of math to figure out the other parts
        total_pages = int(math.ceil(total_records / recordsPerPage)) + 1
        if(page  < total_pages): 
            next_page = page + 1
        else:
            next_page = 0
            
        if(page > 1): 
            prev_page = page - 1
        else:
            prev_page = 0
            
        obj_response_meta = {}   
        obj_response_meta['totalRecords']   = total_records
        obj_response_meta['totalPages']     = total_pages
        obj_response_meta['currentPage']    = page
        obj_response_meta['nextPage']       = next_page
        obj_response_meta['prevPage']       = prev_page
        obj_response_meta['recordsPerPage'] = recordsPerPage
        #obj_response_meta['query']          = sql
        
        return obj_response_body, obj_response_meta, SUCCESS

def get_question_coding_history(user, questionId, completionId = False, characteristicSetId = False):
    """
    Get a history list of all of the codings made for a question by 
    the currently logged in user or the user from the completion record"""
    
    if completionId:
        completion = models.Completion.objects.get(pk=completionId)
        for_user = completion.user
    else:
        for_user = user
    
    if characteristicSetId is False:
        characteristicSetId = for_user.profile.default_characteristic_set_id
    
    charset  = models.CharacteristicSet.objects.get(pk = int(characteristicSetId))
    question = models.Question.objects.get(pk=int(questionId))
    
    obj_response_body  = []
    last_coded_char_id = None
    characteristic     = None
    choice             = None
    choice_text        = None
    
    
    first = 1
    for branch in question.iter_branches(user=for_user, charset=charset):
        if branch:
            
            if str(branch.label.name) == 'True':
                choice_text = branch.coding_choice
            else:
                choice_text = branch.label.name
                
        
            characteristic = branch.label.characteristic
            choice = branch.coding_choice
            
            last_coded_char_id = branch.label.characteristic.id

        
        elif last_coded_char_id:
            from_characteristic = models.Characteristic.objects.get(pk=last_coded_char_id)
            branch = next_branch(from_characteristic, for_user, question, charset)
            if branch is not None:    
                characteristic = branch.to_characteristic
                choice = ''
                choice_text = ''
                
       
        if characteristic:        
            obj_response_body.append({'characteristic'   : str(characteristic),
                                      'code'             : choice,
                                      'choice'           : choice_text,
                                      'questionId'       : question.id,
                                      'characteristicId' : characteristic.id,
                                      'url'              : URL.coding(question.id, characteristic.id)
                                             })
        
    return obj_response_body, {}, SUCCESS


def next_branch(from_characteristic, user, question, charset):
    if from_characteristic.is_categorical():
        #For categorical lookups, the choice is important
        #in determining the correct label and branch
        from_coding = models.Coding.objects.get(user=user,
                                             question=question,
                                             characteristic=from_characteristic.id)
        label = models.Label.objects.get(code = from_coding.choice,
                                         characteristic = from_characteristic)
    
    elif from_characteristic.widget.name == 'just_a_text':
        # just_a_text widgets don't have choices
        # the "question" intro characteristic for example is just_a_text 
         
        label = get_label(from_characteristic) 
    else:
         
        label = get_label(from_characteristic) 
        #label.code = from_coding.choice
     
    return get_branch(charset.id, label)
     
     

def get_coding(user, questionId, characteristicId = False, \
               fromCharacteristicId = False, beforeCharacteristicId = False, \
               completionId = False,characteristicSetId = False ):
    """
    Get a coding made by a user for a question characteristic. 
    If the coding does not yet exist, then we return an object with information 
    about the characteristic and possibly a link to a suggestion for the coding
    If called without a characteristic id, then the next uncoded characteristic 
    for a question will be given, unless fromCharacteristicId is specified. In that case
    the coding after fromCharacteristicId will be returned
    """
    if completionId:
        for_user = models.Completion.objects.get(pk=completionId).user
    else:
        for_user = user
    
    if characteristicSetId is False:
        characteristicSetId = for_user.profile.default_characteristic_set_id 
    
    charset = models.CharacteristicSet.objects.get(id=characteristicSetId)
    
    question = models.Question.objects.get(pk=int(questionId))
    
    start_characteristic = models.Characteristic.objects.get(short_name='domain')
    complete_characteristic = {'characteristicName'        : 'Completed',
                                      'characteristicShortName'   : 'complete',
                                      'characteristicDesc'        : 'This coding is complete',
                                      'characteristicWidget'      : 'just_a_text',
                                      'questionId'                : question.id,
                                      }  
    
    #Determine the characteristic to return
    if not characteristicId:
       
        if fromCharacteristicId:
            #We get the next coding after fromCharacteristicId
            #First we look up the coding made for the characteristic
            #in order to get the label and branch
            #if there is a branch for the label (choice) then
            #we return the to_characteristic of that branch as 
            #the next characteristic
            
            from_characteristic = models.Characteristic.objects.get(pk=fromCharacteristicId)
            
            branch = next_branch(from_characteristic, for_user, question, charset)
            
            if branch is not None:
                ##The next characteristic to code is the branch to_characteristic
                characteristic = branch.to_characteristic
                 
            else:
                #Last - We have reached the end, so we send an object to 
                #indicate that the question is completely coded
                obj_response_body =  complete_characteristic
                              
                question.set_completion(for_user, charset, True)
                    
                return obj_response_body, {}, SUCCESS
            
        elif beforeCharacteristicId:
            
            prev_char_id = None
            
            #We return the coding just before the beforeCharacteristicId
            for branch in question.iter_branches(user=for_user, charset=charset):
                if branch and int(branch.label.characteristic.id) == int(beforeCharacteristicId):
                    break;
                elif branch:
                    prev_char_id = branch.label.characteristic.id 
            
            if prev_char_id is not None:
                characteristic = models.Characteristic.objects.get(pk=prev_char_id) 
            else:
                #Default to the first char
                characteristic = start_characteristic
                
        else:
            #Since there is no fromCharacteristicId or beforeCharacteristicId, the ui is asking the server
            #to show the next characteristic. It seems like the most useful would be to 
            #return the first char for questions with no codings, the next char to 
            #code for questions with some codings, or complete for fully coded questions
            
            last_branch = None
            #Figure out the next uncoded
            for branch in question.iter_branches(user=for_user, charset=charset):
                if branch:
                    last_branch = branch
               
            
            if last_branch:    
                from_characteristic = last_branch.label.characteristic
                branch = next_branch(from_characteristic, for_user, question, charset)
                if branch is not None:
                    ##The next characteristic to code is the branch to_characteristic
                    characteristic = branch.to_characteristic
                else:
                    #Last - We have reached the end, so we send an object to 
                    #indicate that the question is completely coded
                    obj_response_body =  complete_characteristic
                    question.set_completion(for_user, charset, True)
                    return obj_response_body, {}, SUCCESS
            else:
                characteristic = start_characteristic
            
    #A charcteristic id was specified so we use that directly
    else:  
        #In this case we do not update completeness, since this was 
        #a get request for a clicked coding and no codings were changed just before this request  
        characteristic = models.Characteristic.objects.get(pk=int(characteristicId)) 
   
    #Here we see if there is a suggestion available for this characteristic
    try:
        suggestion = models.CodingSuggestion.objects.get(question=question, characteristic=characteristic)
        suggestion_value        = suggestion.value
        has_suggestion          = True
        suggestion_explanation  = suggestion.explanation
        has_explanation         = suggestion.explanation != None
    except models.CodingSuggestion.DoesNotExist:
        suggestion_value          = None
        suggestion_explanation    = None
        has_suggestion            = False
        has_explanation           = False
          
    obj_response_body =  {'id'                        : '',
                          'questionId'                : question.id,
                          'characteristicId'          : characteristic.id,
                          'characteristicName'        : characteristic.name,
                          'characteristicShortName'   : characteristic.short_name,
                          'characteristicDesc'        : textile.textile(characteristic.desc),
                          'characteristicWidget'      : characteristic.widget.name,
                          'hasSuggestion'             : has_suggestion,
                          'suggestion'                : suggestion_value,
                          'suggestionExplanation'     : suggestion_explanation,
                          'hasExplanation'            : has_explanation,
                          'autoFillSuggestion'        : characteristic.auto_fill_suggestion,    
                          'hasBeenAnswered'           : False,
                          'choice'                    : '',
                          'user'                      : for_user.id,
                          'updatedOn'                 : '',
                          'secondsTaken'              : '',
                          'url'                       : URL.coding(question.id, characteristic.id)}  
    
    try:
       
                                      
        coding = models.Coding.objects.get(user=for_user, question=question, characteristic=characteristic)
        obj_response_body['id']             = coding.id,
        obj_response_body['choice']         = coding.choice
        obj_response_body['updatedOn']      = str(coding.updated_on)
        obj_response_body['secondsTaken']   = coding.seconds_taken
        obj_response_body['hasBeenAnswered']= True
                               
    except models.Coding.DoesNotExist:
        coding = None
        
    if  characteristic.widget.name == 'radiobuttons':
        choice_options = []
        for label in characteristic.label_set.all():
            if coding is not None and str(label.code) == str(coding.choice):
                selected = True
            else:
                selected = False
            choice_options.append({'labelId'        : label.id, 
                                   'labelName'      : label.name,
                                   'labelSelected'  : selected,
                                   'labelCode'      : label.code })
        obj_response_body['choiceOptions'] = choice_options  
        
    return obj_response_body, {}, SUCCESS


def update_coding(user, obj_request_body, questionId, characteristicId, characteristicSetId = False):
    
    question       = models.Question.objects.get(pk=int(questionId))
    characteristic = models.Characteristic.objects.get(pk=int(characteristicId))
    
    obj_response_body = obj_request_body    
     
    if characteristicSetId is False:
        characteristicSetId = user.profile.default_characteristic_set_id 
    
    charset = models.CharacteristicSet.objects.get(id=characteristicSetId)
     
    try:
        #simulate the request object for the moment
        characteristic.is_valid_choice(obj_request_body['choice'], question, user) 
    except Exception as error:
        meta = {}
        error_key     = 'InvalidCode'
        error_message = str(error) 
        return obj_response_body, meta, FAILED, error_key, error_message
     
    coding = models.Coding.objects.get_or_create(user=user, \
             question=question, characteristic=characteristic)[0]
    coding.choice = obj_request_body['choice']
    coding.seconds_taken = obj_request_body['secondsTaken']
   
    coding.save(charset=charset)
        
    obj_response_body['id'] = coding.id
       
    #Just mark the completion record as out of date
    #Whenever a coding is saved.
    #This happens in the coding save method  
    #So none of the below work is taking place at the moment 
           
    #To speed things up, we send back the modified object
    #as it is not used in the ui after the save there is no need
    #to call get_coding to refresh the object from the db
    return obj_response_body, {}, SUCCESS

def get_study(user, studyId):
    """Get a study"""
    study = models.Study.objects.get(pk=studyId) 
    
    #Do some permission checking 
    if not study.can_access(user):
        raise views_ui_exceptions.ServiceError(views_ui_exceptions.no_permission, \
                                                    'Operation not permitted');
    
    
    obj_response_body = {'id'   : study.id,
                         'name' : study.name,
                         'url'  : URL.study(study.id)}
    
    return obj_response_body, {}, SUCCESS

def create_or_update_study(user, obj_request_body, studyId = False):
    """Create or update a study for a user"""
    if not studyId:
        #If there is no study id, we create a new study
        study = models.Study(created_by=user)
    else:
        study = models.Study.objects.get(pk=studyId)
        #Do some permission checking 
        if not study.can_edit(user):
            raise views_ui_exceptions.ServiceError(views_ui_exceptions.no_permission, \
                                                    'Operation not permitted');
        
        
    study.name= obj_request_body['name']
    study.save()
    
    return get_study(user, study.id )
    

def delete_study(user, studyId):
    """Delete a study"""
    study = models.Study.objects.get(pk=studyId)
    
    if not study.can_delete(user):
        raise views_ui_exceptions.ServiceError(views_ui_exceptions.no_permission, \
                                                    'Operation not permitted');
    
    obj_response_body = get_study(user, studyId)[0]
    study.delete()
    
    meta = {} 
    return obj_response_body, meta, SUCCESS
