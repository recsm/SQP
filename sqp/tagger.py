#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cPickle import load
from sqp_project.sqp.nlp_tools import word_tokenize, sent_tokenize, not_empty
from django.conf import settings

from sqp_project.sqp.log import logging

try:
    import treetaggerwrapper
    from treetaggerwrapper import TreeTaggerError
except:
    logging.debug("Could not import treetaggerwrapper!")

#The filename part below is currently unused
tagger_dict = {
   'en' : {  'filename':                '', 
             'noun_tag_startswith':     'NN', 
             'tt_language_code' :       'en'},
            
   'nl'   : {'filename':                '', 
             'noun_tag_startswith':     'noun', 
             'tt_language_code' :       'nl'},
            
   'es' : {  'filename':                '', 
             'noun_tag_startswith':     'nc', 
             'tt_language_code' :       'es'},
            
   'ca' : {  'filename':                '', 
             'noun_tag_startswith':     'N5',
             'tt_language_code' :       'ca'},
            
   'de' : {'filename':                  '', 
            'noun_tag_startswith':      'NN', 
            'tt_language_code':         'de'},
            
   'fr' : {'filename':                  '', 
           'noun_tag_startswith':       'NOM',
           'tt_language_code':'         fr'},
            
   'it' : {'filename':                  '', 
           'noun_tag_startswith':       'NOM',
           'tt_language_code':          'it'},
            
   'el' : {'filename':                  '', 
           'noun_tag_startswith':       'No',
           'tt_language_code':          'el'},
            
   'ru' : {'filename':                  '', 
           'noun_tag_startswith':       'Nc',
           'tt_language_code':          'ru'},
           
   'et' : {'filename':                  '', 
           'noun_tag_startswith':       'S.com',
           'tt_language_code':          'et'},
   
   'bg' : {'filename':                  '', 
           'noun_tag_startswith':       'Nc',
           'tt_language_code':          'bg'},
           
   'pt' : {'filename':                  '', 
           'noun_tag_startswith':       'NOM',
           'tt_language_code':          'pt'},
           
   'gl' : {'filename':                  '', 
           'noun_tag_startswith':       'NOM',
           'tt_language_code':          'gl'},
}


path = settings.TAGGER_DIR

def tag(sent, language_iso2='en'):
    # first try treetagger:
    #print "Trying tree tag with ", lan
    try:
        tagger = treetaggerwrapper.TreeTagger(\
               TAGLANG=language_iso2,
               TAGDIR = settings.TAGGER_DIR,
               TAGINENC = 'utf8',
               TAGOUTENC = 'utf8')
        res = tagger.TagText(sent, encoding='utf8')
        res = [tuple(r.decode('utf8').split(u"\t")[0:2]) for r in res]
        return(res)
    except TreeTaggerError, err:
        raise Exception( "Tree tagger returned an error: %s" % str(err) )
        
#   try: # don't try this anymore; too much memory consumption.
#       input = open(path + tagger_dict[lan]['filename'], 'rb')
#       tagger = load(input)
#       input.close()
#       res = tagger.tag(sent)
#       del tagger
#       return(res)
#   except Exception, err:
#      logging.debug( "Could not tag at all: %s..." % str(err) )
#      return ''


def tagged_sents_to_table(tagged_sents, noun_tag=None):
    "Formats result of tagging as HTML table"
    sents_table = u'<table>'
    for sent in tagged_sents:
        for word in sent:
            sents_table += u'<tr><td'
            if word[1].lower().startswith(noun_tag): 
                sents_table += u' style="font-weight: bold;"'
            sents_table +=  u'>' + word[0] + '</td>'
            sents_table += u'<td> ' + word[1] + u'</td></tr>'
            
    sents_table += '</table>'
    return sents_table

def count_nouns(s, language_iso2='en'):
    
    words = filter(lambda x: x!=[], map(word_tokenize, sent_tokenize(s, language_iso2)))
    tagged_sents = [tag(word_list, language_iso2) for word_list in words]
    tagged_sents = [s for s in tagged_sents if s]
    if not tagged_sents: 
        raise Exception('Count nouns not available for language %s' % language_iso2 )

    noun_tag = tagger_dict[language_iso2]['noun_tag_startswith'].lower()
    return [sum([sum([(word_pair[1].lower().find(noun_tag) != -1) \
               for word_pair in sent]) for sent in tagged_sents if sent]),
               tagged_sents_to_table(tagged_sents, noun_tag)]
   