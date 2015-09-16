#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO:
# - provide a checking mechanism for the whole interview (no loops, should reach all characteristics indicated)
# Bring back export to CSV, new one in similar format as WinSQP for Compare?

# - use questions & variables PDF appendix to show info about item (protoTip)
# - add rfa & intro text for 18 ESS2 French France questions


import csv
import time
import datetime

import cStringIO as StringIO

#from sqp_project.memory_usage import print_memory_usage

import difflib

from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect

from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from sqp_project.sqp.models import *  # TODO: fix namespace pollution
from sqp_project.sqp import nlp_tools

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, \
    user_passes_test

from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ModelForm
from django import forms

from sqp_project.sqp import suggestions
from django.conf import settings


class AllItemForm(forms.Form):
    items = forms.ModelMultipleChoiceField(Item.objects.all(),
            widget = FilteredSelectMultiple("Items", False, attrs={'rows':'15'}))


class CompareCulturesForm(forms.Form):

    from_country = forms.ModelChoiceField(UsedCountry.objects.all())
    from_language = forms.ModelChoiceField(Language.objects.all())
    from_coder = forms.ModelChoiceField(User.objects.all())

    to_country = forms.ModelChoiceField(UsedCountry.objects.all())
    to_language = forms.ModelChoiceField(Language.objects.all())
    to_coder = forms.ModelChoiceField(User.objects.all())


def char_list(request):
    """Scans the questions and prints out a list of used chars
    """   

    chars = {}
    for q in Question.objects.iterator():
        
        text = ''
        if q.rfa_text is not None:
            text += q.rfa_text
        if q.introduction_text is not None:
            text += q.introduction_text
        if q.answer_text is not None:
            text += q.answer_text
        
        for c in text:
            if ord(c) not in range(65,91) + range(97,123) + range(44,47):
                try:
                    chars[ord(c)] += 1
                except:
                    chars[ord(c)] = 1
   
    chars_explained = {
                       9: 'ht character tabulation ctrl-i',
                       10: 'lf line feed ctrl-j',
                       13: 'cr carriage return ctrl-m',
                       32: 'space',
                       95: 'low line',
                       171: 'left-pointing double angle quotation mark',
                       172: 'not sign',
                       180: 'acute accent',
                       187: 'right-pointing double angle quotation mark',
                       189: 'vulgar fraction one half',
                       8211 : 'en dash',
                       8216 : 'left single quotation mark',
                       8217 : 'right single quotation mark',
                       8220 : 'left double quotation mark',
                       8221 : 'right double quotation mark',
                       8222 : 'double low-9 quotation mark',
                       8230 : 'horizontal ellipsis'
                       }

    html = '<table border=1 cellpadding=10>'
    html += '<tr><th>Unicode code point</th><th>Unicode</th><th>Count</th><th>Representation</th><th>Explained</th></tr>'
    
    
    for char_code in sorted(chars.keys()):
        
        if char_code in chars_explained.keys():
            explained = chars_explained[char_code]
        else:
            explained = ''
            
        html += u'<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (char_code, hex(char_code), chars[char_code], unichr(char_code), explained)
        
    html += '</table>' 
        
    return HttpResponse(html)

@login_required
def compare_items(request):
    if request.POST: 
        all_item_form=AllItemForm(request.POST)
        compare_form = CompareCulturesForm(request.POST)
    else:
        all_item_form = AllItemForm()
        compare_form = CompareCulturesForm()

    if request.POST and (all_item_form.is_valid() and compare_form.is_valid()):
        return compare(request, data = dict(compare_form.data.lists()))

    return render_to_response("sqp/compare_choose.html", 
            {'item_form':  all_item_form,
             'compare_form': compare_form,
        })

class Comparison:
    """Allows for comparison of codes for one item in different country/languages"""
    def __init__(self, request, item, country_from, language_from, user_from, 
            country_to, language_to, user_to, characteristicSetId=False):
        """Take item and culture information and set up the comparison
        for use with difflib"""
        self.item = Item.objects.get(pk = item)
        self.request = request
        
        if characteristicSetId is False:
            characteristicSetId = request.user.profile.default_characteristic_set_id
         
        self.charset = CharacteristicSet.objects.get(id=characteristicSetId) 

        # The following may raise an Exception:
        self.question_from = Question.objects.get(item = item, 
            language = language_from, country = country_from)
        self.question_to = Question.objects.get(item = item, 
            language = language_to, country = country_to)

        self.user_from = user_from
        self.user_to = user_to

        self.init_lines()
        self.differ = difflib.HtmlDiff()

    def init_lines(self, num_tabs = 5):
        """Create lists of strings (coding histories) showing the choices"""
        self.from_lines = [] # will contain list of strings
        self.to_lines = []

        # Loop over branches and add one line of the form 
        #   "Characteristic name<tabs>choice made" to the list
        for branch in self.question_from.iter_branches(user=self.user_from, 
                charset = self.charset):
            if branch:
                self.from_lines.append(self.make_line(branch))

        for branch in self.question_to.iter_branches(user=self.user_to, 
                charset = self.charset):
            if branch:
                self.to_lines.append(self.make_line(branch))

    def make_line(self, branch):
        return """<table class="choice"><tr><td class="characteristic">%s</td>
            <td class="choice">%s</td></tr></table>""" % \
            (branch.label.characteristic.name,
            branch.label.name == 'True' and \
                    branch.coding_choice or branch.label.name)

    def as_html(self):
        """Return an HTML table as formatted by difflib.HtmlDiff"""
        html = self.differ.make_table(self.from_lines, self.to_lines, 
                fromdesc = "%s by %s" % (unicode(self.question_from), 
                    self.user_from.username), 
                todesc = "%s by %s" % (unicode(self.question_to), 
                    self.user_to.username))
        html = html.replace('&lt;', '<')
        html = html.replace('&gt;', '>')
        html = html.replace('&nbsp;', ' ')
        return html

@login_required 
def compare(request, data):
    comparisons = []

    from_language = Language.objects.get(pk = data['from_language'][0])
    to_language = Language.objects.get(pk = data['to_language'][0])
    from_country = Country.objects.get(pk = data['from_country'][0])
    to_country = Country.objects.get(pk = data['to_country'][0])

    from_user = User.objects.get(pk = data['from_coder'][0])
    to_user = User.objects.get(pk = data['to_coder'][0])
    
    for item in data['items']:
        try: 
            new_comparison = Comparison(request, item, from_country, from_language, 
                 from_user, to_country, to_language, to_user)
            newstring = new_comparison.as_html()
        except Exception, err:
            newstring = """<div class="error">An error occurred trying 
                to compare: %s</div>""" % str(err)
        comparisons.append(newstring)

    return render_to_response("sqp/compare_view.html", {
        'comparisons' : comparisons, })




def get_question(pk, request):
    """Retrieve a Question object, annotating it with completion data from 
        the database and Related objects Item, Study, Language and Country.
        using the Question, its complete attribute and Related objects will 
        only result in 1 total database hit."""
    sql = "SELECT COUNT(*) > 0 FROM sqp_completion WHERE sqp_completion.question_id = sqp_question.id AND sqp_completion.characteristic_set_id = %d AND sqp_completion.user_id = %d AND sqp_completion.complete = TRUE" % (int(request.session['characteristic_set']), request.user.id)
    question_qset = Question.objects.filter(pk = pk).\
        select_related('item', 'item__study', 'language', 'country').\
        extra(select={'complete': sql},)
    if question_qset: return question_qset[0]
    return None

def please_choose(count):
    return([('', "All applicable (%s)" % str(count)), ])

def byrow(lod, keylist):
    """Converts a list of dictionaries to a list of lists using the
    values of the dictionaries. Assumes that each dictionary has the
    same keys. 
       lod: list of dictionaries
       keylist: list of keys, ordered as desired
       Returns: a list of lists where the inner lists are rows. 
         i.e. returns a list of rows. """

    return [[row[key] for key in keylist] for row in lod]

class OptionsForm(forms.Form):
    """Program options form"""
    characteristic_set = forms.ChoiceField()


def copy_form(request, question_id):
    """View for Ajax request of copy form."""
    
    question = get_question(question_id, request)
    copy_form = get_copy_form(request, question)

    return render_to_response('sqp/copy_form.html',
            {#'question': question,
             #'request' : request,
             'copy_form': copy_form}
             , context_instance=RequestContext(request))

def get_one_listed_question(request, question_id):
    """View for Ajax request of one question list item"""
    question = get_question(question_id, request)

    return render_to_response('sqp/one_listed_question.html',
            {'question': question,
             'request' : request}
             , context_instance=RequestContext(request))

def render_to_pdf(template_src, context_dict):
    import ho.pisa as pisa
    template = loader.get_template(template_src)
    context = Context(context_dict)
    html  = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("utf-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % cgi.escape(html))

def codebook_overview(request):
    chars = Characteristic.objects.iterator()
    return render_to_response('sqp/overview.html',
        { 'characteristics' : chars,
        })
        
def codebook(request, charset_id):
    "Shows a codebook representing the characteristic set."

    charset = get_object_or_404(CharacteristicSet, pk = charset_id)
    start_from = 'question'
    if 'start_from' in request.GET: start_from = request.GET['start_from']
    
    chars = [] # to preserve order
    def append_char(char): chars.append(char)
    charset.apply_to_width(apply_func=append_char, 
            done=set(), done_chars=set())

    if 'pdf' in request.GET: render_func = render_to_pdf
    else: render_func = render_to_response
        
    return render_func('sqp/codebook.html',
        {'charset' : charset,
         'characteristics' : chars,
         'start_from':start_from,
        })
        
def view_charset(request, charset_id):
    "Shows a graph representing the characteristic set."
    charset = get_object_or_404(CharacteristicSet, pk = charset_id)
    start_from = 'question'
    if 'start_from' in request.GET: start_from = request.GET['start_from']
    
    img_path = os.path.split(charset.to_graph(start_from = start_from))[1]

    return render_to_response('sqp/view_charset.html',
        {'charset' : charset,
        'characteristics' : charset.get_characteristics(),
        'start_from':start_from,
         'img_path' : img_path
        }, 
        context_instance=RequestContext(request))


def get_question_form(selection_dict, studies, languages, countries):
    """Create a question form based on filterings applied 
        in list_questions and return a bound or unbound Form"""
    study_choices = [(study.id, study.name) for study in studies.iterator()]
    study_choices[0:0] = please_choose(len(study_choices))

    language_choices = [(lan.id, lan.name) for lan in languages.iterator()]
    language_choices[0:0] = please_choose(len(language_choices))

    country_choices = [(c.iso, c.name) for c in countries.iterator()]
    country_choices[0:0] = please_choose(len(country_choices))

    class QuestionForm(forms.Form): 
        """Form for choice of study (ESS round,...), language and country."""
        study = forms.ChoiceField(study_choices)
        language =  forms.ChoiceField(language_choices)
        country =  forms.ChoiceField(country_choices)

    if selection_dict: return QuestionForm(selection_dict)
    return QuestionForm()
    

def list_questions(request):
    "Show the list of questions"
    country_iso, study_id, language_id, edit_question = [None]*4
    selection_dict = {}

    if 'characteristic_set' in request.POST: # from options_form
        request.session['characteristic_set'] = request.POST['characteristic_set']

    # Figure out characteristic set to be used 
    if 'characteristic_set' not in request.session:
        request.session['characteristic_set'] = CharacteristicSet.objects.filter(\
                coders = request.user)[0].id # default is first in the list

    # Select only the languages this User has been linked to
    language_qset = request.user.language_set
    # Select only the studies this User has been linked to
    study_qset = request.user.study_set
    # Select only the characteristic sets this User has been linked to
    charsets = request.user.characteristicset_set.all()
    # Select only the questions that this user has been assigned to 
    #   select_related(2) here speeds up the template rendering time by a factor 2
    #   because q.item.concept is used there. Could be improved by reading into a [].
    sql = "SELECT COUNT(*) > 0 FROM sqp_completion WHERE sqp_completion.question_id = sqp_question.id AND     sqp_completion.characteristic_set_id = %d AND sqp_completion.user_id = %d AND sqp_completion.complete = TRUE" % (int(request.session['characteristic_set']), request.user.id)

    question_qset = Question.objects.filter(language__coders = request.user).\
        filter(item__study__coders = request.user).select_related(depth = 2).\
        extra(select={'complete': sql},)

    country_qset = Country.objects.filter(question__language__in = \
           language_qset.all()).distinct()

    # If a subselection has been made by user, filter the list of questions
    if request.method == 'GET':
        if 'characteristic_set' in request.GET:
            change_characteristic_set(request, request.GET['characteristic_set'])

        if 'study' in request.GET and request.GET['study']:
            # Filter questions and languages on study
            study_id = int(request.GET['study'])
            question_qset = question_qset.filter(item__study__id = study_id)
            language_qset = language_qset.filter(question__item__study__pk = \
                study_id).distinct()
        else:  # Select default study to limit the number of choices
            study_id = 1

        if 'language' in request.GET and request.GET['language']:
            language_id = int(request.GET['language'])
            question_qset = question_qset.filter(language = language_id)
            country_qset = country_qset.filter(question__language = language_id).\
                distinct()

        if 'country' in request.GET and request.GET['country']:
            country_iso = request.GET['country']
            # Only make subselection if country is in language, 
            #   otherwise it might be leftover
            if country_iso in [country.iso for country in country_qset.iterator()]:
                question_qset = question_qset.filter(country = country_iso)
        
        if 'edit_question' in request.GET and request.GET['edit_question']:
            edit_question = int(request.GET['edit_question'])
        else:
            for qst in question_qset.iterator(): edit_question = qst.id; break

        selection_dict = { 'country' : country_iso, 
            'study' : study_id, 'language': language_id, 
            'edit_question' : edit_question}

    question_form = get_question_form(selection_dict, study_qset, 
        language_qset, country_qset)

    # Options are stored in the session and used to initialize an OptionsForm
    options_form = OptionsForm(request.session)
    charset_choices = [(charset.id, charset.name) for charset in charsets]
    options_form.fields['characteristic_set'] = forms.ChoiceField(charset_choices)

    # Finally apply this rather impressive ordering rule:
    question_qset = question_qset.order_by('item__study', 'country', 
            'language', 'item__admin_letter', 'item__admin_number', 'item__id')

    ie = request.META['HTTP_USER_AGENT'].find('MSIE') > 0
    
    return render_to_response('sqp/list_questions.html', {
        'questions': question_qset,
        'question_form': question_form,
        'options_form': options_form,
        'languages': language_qset,
        'countries': country_qset,
        'request': request,
        'selection_dict':selection_dict,
        'ie': ie,
        }, context_instance=RequestContext(request))

def change_characteristic_set(request, set_id):
    """ Changes the current characteristic_set to the one with set_id.
        The session variable 'characteristic_set' is set to this id
        if all is in order. """
    
    # check existence or raise 404 (int is validated in regex urls.py)
    cs = get_object_or_404(CharacteristicSet, pk=int(set_id)) 

    # Check whether this user is allowed to see this characteristic set:
    if request.user in cs.coders.all():
        request.session['characteristic_set'] = int(set_id)
    return

def get_copy_form(request, question):
    """Returns a form with studies, languages, items, and coutnries
    available for this user. Cannot be a global class because it depends
    on request.user.
    If the form was just posted, filter the items by study and bind the form"""
    initial = None
    if request.method == 'POST' and 'action' in request.POST and \
        request.POST['action'] == 'copy':
        study = request.POST['study'] 
    else: # not a posted form
        study =  question.item.study.id
        initial = {'study': study,
            'item': '-1', 'country': question.country.iso,
            'language': str(question.language.id)}

    lans = Language.objects.filter(coders = request.user)
    studies = Study.objects.filter(coders = request.user)
    questions = Question.objects.filter(language__in = lans).\
        select_related('item', 'item__study', 'language', 'country').distinct()
    items = Item.objects.filter(question__language__in = lans).\
                filter(study__in = studies).distinct()

    cnts = Country.objects.values('iso', 'name').\
           filter(question__language__in = lans).distinct()
    item_list = [('-1', 'Please choose...')]
    item_list.extend(byrow(items.values('id', 'name'), ['id', 'name']))

    class CopyForm(forms.Form):
        """Form that allows user to copy choices from another Questions"""
        language = forms.ChoiceField(byrow(lans.values('id', 'name'),
                    ['id', 'name']))
        study = forms.ChoiceField(byrow(studies.values('id', 'name'),
             ['id', 'name']))
        item = forms.ChoiceField(item_list)
        country = forms.ChoiceField(byrow(cnts.values('iso', 'name'), 
                    ['iso', 'name']))

    return initial and CopyForm(initial = initial) or CopyForm(request.POST)


def code_rfa(request, question, characteristic, 
        message="", message_class="warning"):
    """The first characteristic displayed is a special coding page
       for the introduction, request for an answer and categories."""
    # There should be exactly one label associated with the 
    #  characteristic named 'Question'
    label_id = Label.objects.get(characteristic = characteristic).id
    try: 
        intro_desc = Characteristic.objects.get(\
                name = 'Introduction available?').desc
    except: intro_desc = ''

    copy_form =  get_copy_form(request, question)
    if request.method == 'POST' and 'copy_submit' in request.POST:
        # The copy form was submitted on purpose (user clicked button)
        message, message_class = question.copy_codes(request)

    return render_to_response('sqp/display_characteristic.html',
            {'message' : message, 
             'message_class' : message_class, 
             'history': question.iter_branches(request=request),
             'question' : question,
             'characteristic' : characteristic,
             'start_time' : time.time(),
             'copy_form':copy_form,
             'tips':tips, #from sqp.models
            })

def apply_suggestion(request, question, characteristic):
    """Look for the function specified in sqp_project.sqp.suggestions
       and call it with the arguments, returning its result"""
    
    if characteristic.suggestion not in dir(suggestions):
        return """(Warning: A suggestion should be present but no function was 
                found.)"""
                
    return eval('suggestions.' + characteristic.suggestion + \
           '(request, question, characteristic)' )


def display_characteristic(request, question, characteristic, 
        message="", message_class='warning'):
    """Render the html form for this characteristic and question"""
    if characteristic.short_name == 'question': #special case
        return code_rfa(request, question, characteristic, 
                message, message_class)

    suggestion = characteristic.suggestion and \
        apply_suggestion(request, question, characteristic) or ''
    annotate_characteristic(request, characteristic, question)
    previous_characteristic = question.get_previous_characteristic(request, 
        characteristic)
    return render_to_response('sqp/display_characteristic.html',
            {'message' : message, 
             'message_class' : message_class,
             'question' : question,
             'history': question.iter_branches(request=request),
             'characteristic' : characteristic,
             'previous_characteristic' : previous_characteristic,
             'start_time' : time.time(),
             'suggestion' : suggestion,
             'tips':tips, #from sqp.models
            })

def display_overview(request, question):
    """Overview of question choices made"""
    question.update_completion(request)
    
    return render_to_response('sqp/save_success.html',
            {   'question' : question,
                'history': question.iter_branches(request=request),
                'next_id' : question.get_next_question_id() })

def save_choice(request, question, characteristic, label, elapsed):
    """Validate and save the choice made for this characteristic. Return
       a message describing what happened. Characteristic.is_valid_choice() 
       will raise exception if all is not well"""
    
    # validate choice, raises InvalidCode if not valid (caught in code())
    characteristic.is_valid_choice(label.code, question, request) 

    (coding, created) = Coding.objects.get_or_create(question=question, \
                            characteristic=characteristic, user=request.user)
    coding.choice = label.code.strip()
    coding.seconds_taken = elapsed
    # save choice and set msg
    coding.save()

    message = "Successfully " + (created and 'created' or 'saved') + \
              " coding."
    question.update_completion(request)
    return message   

def get_branch(request, label):
    """Retrieve the branch associated with the current CharacteristicSet
       and linked to the Label passed. If found return it, if not None."""
    cset_id = request.session['characteristic_set']
    try:
        return Branch.objects.get(label = label, 
                characteristicset__id = cset_id)
    except Branch.DoesNotExist: # no branch with that label in that cSet
        return None

def get_label(request, characteristic):
    """Given a POST request and a non-categorical characteristic, determine
       which label to apply, and return it."""
    labels = Label.objects.filter(characteristic = characteristic, compute = True)
    return labels[0] # TODO: evaluate rules (now just taking the first found)

def annotate_characteristic(request, characteristic, question):
    """Adds the coding, if any, corresponding to the current user, 
        characteristic, and question as an attribute to the characteristic
        and returns the annotated characteristic."""
    try:
        characteristic.coding = Coding.objects.get(user = request.user, 
                characteristic = characteristic, question = question)
    except Coding.DoesNotExist: pass # too bad, do nothing

def code(request, question_id):
    """ Display each characteristic on a separate page. 
        After submit, validate choice, save it, and check 
        for routing in Label.skip_to to find the next characteristic.
        When all characteristics are coded, display an overview
            with the option of changing any one of them.
        If no information is given, display the first characteristic 
            to be coded.
        All the while show the introduction, rfa, and answer categories."""
    stop_time = time.time() # for calculating seconds elapsed
    question = get_question(question_id, request)

    if request.method == 'GET':
        if 'skip_to_char' in request.GET:
            # Clicked one of the history items
            return display_characteristic(request, question, 
                    get_object_or_404(Characteristic, 
                        pk = request.GET['skip_to_char']), '')
        # Nothing, just show the first page
        message = ""
        source = get_object_or_404(Characteristic, short_name="question")
        return code_rfa(request, question, source, message)
    
    if 'action' in request.POST and request.POST['action'] == 'copy':
        # Used the copy form, let code_rfa handle it. The submit is not 
        #   necessarily on purpose by user, that would be 'copy_submit'
        source = get_object_or_404(Characteristic, short_name="question")
        return code_rfa(request, question, source, '')

    if 'smb_prev' in request.POST: 
        # go back to prev. characteristic without saving
        char = Characteristic.objects.get(pk = request.POST['prev_char_id'])
        return display_characteristic(request, question, char, '')

    current_ch = get_object_or_404(Characteristic, 
                    pk = request.POST['characteristic_id'])

    question.save_question_rfa(request)

    if ('change_question_text' in request.POST) and \
       (request.POST['change_question_text'] == '1'): 
        # The form was only submitted to change the question text. 
        # Redisplay the same characteristic again.
        return display_characteristic(request, question, current_ch)
        
    if 'rfa_smb' in request.POST: # source characteristic
        label = get_object_or_404(Label, pk = request.POST['label_id'])
    else: # Not the source 'Question' characteristic
        if current_ch.is_categorical():
            if 'label' not in request.POST:
                return display_characteristic(request, question, current_ch, 
                        "Please make a choice for this characteristic.")
            label = Label.objects.get(code = int(request.POST['label']),
                    characteristic = current_ch)
        elif current_ch.widget.name == 'just_a_text':
            label = get_label(request, current_ch) 
        else:
            label = get_label(request, current_ch) 
            label.code = request.POST['choice']
        try:
            elapsed = stop_time - float(request.POST['start_time'])
            save_choice(request, question, current_ch, label, elapsed)
        except InvalidCode, error:
            # Redisplay the same choice with the error found
            return display_characteristic(request, question, 
                current_ch, str(error))

    # Get Branch associated with this label and CSet
    branch = get_branch(request, label)
    if branch: 
        return display_characteristic(request, question, branch.to_characteristic)
    else: # we got to the end: display overview.
        # TODO: use question.check_codings_complete(request)
        #        to provide information about missing codes
        return display_overview(request, question) 



def logout_view(request):
    "Log out the user"
    clearit = ['resolution', 'countries', 'questions']
    for it in clearit:
        if it in request.session:
            del request.session[it]
    logout(request)
    return render_to_response('sqp/logout_success.html')


        
def export_data(request):
    """Output a spreadsheet with all coded questions to HttpResponse.
       Only codings for characteristics in the current CharacteristicSet
       are written. Only questions with at least one coding are written.
       All coder's codings are written. Variable names for the characteristics
       in the output file are 'char_<characteristic.id>'."""


    #response = HttpResponse(mimetype='text/csv')
    #response['Content-Disposition'] = 'attachment; filename=sqp_codes.csv'
    
   
    #create our csv file
    csvfile = open(settings.MEDIA_ROOT + 'tmp/sqp_codes.csv', "wb")
    
    charset = request.session.get('characteristic_set', default = 1)  
    tnames = []
    #charset = request.session.get('characteristic_set', default = 1)
    branches = Branch.objects.filter(characteristicset = charset)
    for branch in branches:
        short_name = branch.label.characteristic.short_name
        if short_name not in tnames:
            tnames.append(short_name)
           
    question_fieldnames =  ['question_id',
                    'study', 'item_admin', 
                    'item','language', 
                    'country',]       
    fieldnames = []
    fieldnames.extend(question_fieldnames)        
    fieldnames.extend(['coder', 'last_updated_coding'])
    
    #need updated on
    fieldnames.extend(tnames)
    writer = csv.DictWriter(csvfile, fieldnames, restval = ".", #NA
                    extrasaction = 'ignore',
                    dialect='excel', delimiter=';') 

    writer.writerow(dict([(fnam, fnam) for fnam in fieldnames])) # header
    
    for question in Question.objects.select_related('item', 'item__study' 'country', 'language').\
                   order_by('language', 'country', 'item').\
                   all()[2000:2100]:
       
        #get a unique list of coders who have coded a question and loop over it
        for coder in User.objects.filter(coding__question = question).distinct():
            
            last_updated            =  datetime.datetime.fromtimestamp(0)
            rowdict = {}
            rowdict['coder']        = coder
            rowdict['question_id']  = question.id
            rowdict['study']        = question.item.study.id
            rowdict['item_admin']   = question.item.admin
            rowdict['item']         = question.item.name
            rowdict['language']     = question.language.iso
            rowdict['country']      = question.country.iso
           
            #for each coder get all of the codings
            for branch in question.iter_branches(user=coder,charset=charset):
                if branch:
                    if hasattr(branch, 'updated_on') and branch.updated_on > last_updated:
                        last_updated = branch.updated_on
                        
                        
                    rowdict[branch.label.characteristic.short_name] = branch.coding_choice
  
            rowdict['last_updated_coding'] = last_updated
             
            writer.writerow(rowdict)    
    
    csvfile.close()
    return redirect(settings.MEDIA_URL + 'tmp/sqp_codes.csv')

def set_characteristic_set(s):
    # wanted for inexplicable reasons by django.contrib.admin
    pass


def syllable_tool(request):
    """A view used to test NLP"""
    original = ''
    inserted = ''
    key_string = 'English (United States)'

    if request.method == 'POST':
        form_data = request.POST.copy()
        key_string = request.POST['language']
        original = request.POST['original']
        form_data['inserted'] = nlp_tools.show_syllables(original, key_string)
        form = SyllableForm(form_data)
    else:
        form = SyllableForm({'language': key_string})

    num_syllables = nlp_tools.count_syllables(original, key_string)

    return render_to_response('sqp/syllable_tool.html', {
        'num_syllables': num_syllables,
        'form': form,
        'request': request,
        'keystring': key_string,
        })

def get_num_syllables(request):
    """A view used to test NLP"""
    key_string = 'English (United States)'
    if request.method == 'POST':
        try:
            original = request.POST['original']
            key_string = request.POST['language']
            num_syllables = nlp_tools.count_syllables(original, key_string)
        except:
            num_syllables = 'Sorry, could not hyphenate for '\
                 + key_string + '.'
    else:
        num_syllables = ''
    return render_to_response('sqp/get_quantity.html', {'quantity'
                              : num_syllables})

def get_num_words(request):
    """A view used to test NLP"""
    if request.method == 'POST':
        try:
            text = request.POST['original']
            num_words = nlp_tools.count_words(text)
        except:
            num_words = 'error'
    else:
        num_words = ''
    return render_to_response('sqp/get_quantity.html', {'quantity'
                              : num_words})

def get_num_sentences(request):
    """A view used to test NLP"""
    if request.method == 'POST':
        try:
            text = request.POST['original']
            num_sentences = nlp_tools.count_sentences(text)
        except:
            num_sentences = 'error'
    else:
        num_sentences = ''
    return render_to_response('sqp/get_quantity.html', {'quantity'
                              : num_sentences})

def get_num_nouns(request):
    """A view used to test NLP"""
    if request.method == 'POST':
        try:
            text = request.POST['original'].lower()
            key_string = request.POST['language']
            language = key_string.split(' ')[0]
            if language in tagger_dict.keys():
                num_nouns = count_nouns(text, language)
            else:
                num_nouns = 'Sorry, no tagger available for ' + language\
                     + ' ...'
        except:
            num_nouns = 'error (bad querystring?)'
    else:
        num_nouns = ''
    return render_to_response('sqp/get_quantity.html', {'quantity'
                              : num_nouns})

class SyllableForm(forms.Form):
    """A form used for testing the syllable counter"""
    original = forms.CharField(widget=forms.Textarea)
    inserted = forms.CharField(widget=forms.Textarea, required=False)
    language = forms.ChoiceField([[x, x] for x in nlp_tools.hyphenation_keys])


list_questions = login_required(list_questions)
code = login_required(code)

list_questions = user_passes_test(lambda u: u.has_perm('sqp.add_coding'
                                  ))(list_questions)
code = user_passes_test(lambda u: u.has_perm('sqp.add_coding'))(code)


def question_json(request):
    return ajax_render_to('json/question.json')

def questionList_json(request):
    return ajax_render_to('json/questionList.json')


try:
    import json
except:
    from django.utils import simplejson as json

from django.conf import settings 

def ajax_render_to(template_name):
    
    file = open(settings.MEDIA_ROOT + template_name, 'rb')
    try:
        text = file.read()
    finally:
        file.close()
    dict = json.loads(text)
    jsondict = json.dumps(dict)
    return HttpResponse(jsondict, mimetype='application/json')

            