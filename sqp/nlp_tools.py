#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import nltk   # natural language processing toolkit
from sqp_project.hyphenator import Hyphenator  # myspell hyphenator [TODO: implement Hunspell?]
import re
from django.conf import settings

hyphenation_file = {
'Bulgarian (Bulgaria)':'hyph_bg_BG',
'Catalan (Spain)':'hyph_ca_ES',
'Czech (Czech Republic)':'hyph_cs_CZ',
'Danish (Denmark)':'hyph_da_DK',
'Dutch (Netherlands)':'hyph_nl_NL',
'English (United Kingdom)':'hyph_en_GB',
'English (United States)':'hyph_en_US',
'English (Canada)':'hyph_en_CA',
'Estonian (Estonia)':'hyph_et_EE',
'Finnish (Finland)':'hyph_fi_FI',
'French (Belgium)':'hyph_fr_BE',
'French (France)':'hyph_fr_FR',
'Galician (Spain)':'hyph_gl_ES',
'German (Germany)':'hyph_de_DE',
'German (Switzerland)':'hyph_de_CH',
'Greek (Greece)':'hyph_el_GR',
'Hungarian (Hungary)':'hyph_hu_HU',
'Icelandic (Iceland)':'hyph_is_IS',
'Irish (Ireland)':'hyph_ga_IE',
'Italian (Italy)':'hyph_it_IT',
'Lithuanian (Lithuania)':'hyph_lt_LT',
'Norwegian Nynorsk (Norway)':'hyph_nn_NO',
'Norwegian Bokmal (Norway)':'hyph_nb_NO',
'Polish (Poland)':'hyph_pl_PL',
'Portuguese (Brasil)':'hyph_pt_BR',
'Portuguese (Portugal)':'hyph_pt_PT',
'Romanian (Romania)':'hyph_ro_RO',
'Russian (Russia)':'hyph_ru_RU',
'Slovak (Slovakia)':'hyph_sk_SK',
'Slovenian (Slovenia)':'hyph_sl_SI',
'Spanish (Spain)':'hyph_es_ES',
'Swedish (Sweden)':'hyph_sv_SE',
'Ukrainian (Ukraine)':'hyph_uk_UA'}

path = settings.HYPHENATION_DIR
hyphenation_keys = hyphenation_file.keys() 
hyphenation_keys.sort()

re_sent = re.compile(r'[\.\?!]+')
re_sent_greek = re.compile(r'[\.\?;!]+')
re_punct = re.compile(r'[ÃÂ¡ÃÂ¿"ÃÂ«ÃÂ»\?,Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ;:Ã¢ÂÂ/Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ¦\(\)\[\]\{\}\<\>ÃÂ·&*Ã¢ÂÂ¢Ã¢ÂÂ Ã¢ÂÂ¡ÃÂ°\#%Ã¢ÂÂ°Ã¢ÂÂ±ÃÂ¶ÃÂ§~ÃÂ¨\|\.-]+')
re_alt = re.compile(r'[Ã¢ÂÂÃ¢ÂÂ`]+')
re_broken = re.compile(r'-\n')
re_break = re.compile(r'[\r\n]')
re_word = re.compile(r'[ \t]', re.UNICODE)

def not_empty(s):
    return(s != u'')

def sent_tokenize(phrase, lan=""):
    #print lan
    phrase = phrase.strip()
    if (lan != "ell"): 
        sp = re_sent.split(phrase)
    else:  #Greek uses ; as a question mark...
        sp = re_sent_greek.split(phrase)
    sp = filter(not_empty, sp)
    return(sp)

def word_tokenize(sent):
    """ 
    >>> word_tokenize("On an average weekday, how much time, in total, do you \
                      spend watching television? Please use this card to answer.")
    ['On',
     'an',
     'average',
     'weekday',
     'how',
     'much',
     'time',
     'in',
     'total',
     'do',
     'you',
     'spend',
     'watching',
     'television',
     'Please',
     'use',
     'this',
     'card',
     'to',
     'answer']
   
    """
    sent = re_alt.sub(u"'", sent)   # Replace fancy single quotes with '.
    sent = re_broken.sub(u'', sent) # Unless a word has been bro-\nken,
    sent = re_break.sub(u' ', sent) #    replace line breaks with spaces.
    sent = re_punct.sub(u'', sent)  # Remove all punctuation except for '.
    words = re_word.split(sent)
    words = filter(not_empty, words)
    return(words)


def find_key(language):
    if (language not in hyphenation_keys):
        lan = language.split(" ")[0]
        for key in hyphenation_keys: 
            if (key.find(lan)!=-1):
                return key
    return language

def get_hyphenator(language, country):
    hyph = "hyph_%s_%s" % (language.lower(), country.upper())
    try:
        h = Hyphenator(path + hyph + ".dic")
    except IOError:
        # If not found for this combination, try to find a file for the
        #  same language but different country
        alt_langs = [v for v in hyphenation_file.values() \
                 if v.startswith('hyph_%s' % language)]
        try:
            h = Hyphenator(path + alt_langs[0] + ".dic")
        except Exception, err : # if that does not work either
            raise Exception('Hyphenator returned an error %s' %  str(err))  
    
    return h

def count_syllables(s, language="en", country='GB'):
    """Counts syllables using the nltk regexp word tokenizer
      and a hyphenation dictionary from Myspell. 
      Note that hyphenation is not exactly the same as number
      of syllables in all languages (but close).
      Still a problem with apostrophes (they are incorrectly tokenized 
      as words)."""
    #language = find_key(language)      
    
    h = get_hyphenator(language, country)

    words = word_tokenize(s)
    # words = nltk.tokenize.regexp.WordTokenizer().tokenize(s)
    wordsize = [len(h.positions(w))+1 for w in words]
    # num_complex = sum([w>=3 for w in wordsize])    # number of "complex words"
    
    res = [h.inserted(w) for w in words]
    explained = ' '.join(res)
    
    return(sum(wordsize)), explained

def count_words(s):
    """Counts words using nltk tokenizer."""
    words = word_tokenize(s)
    return(len(words))

def count_sentences(s, lan=''):
    """Counts sentences."""
    #tok = nltk.tokenize.punkt.PunktSentenceTokenizer()
    sents = sent_tokenize(s, lan)
    res = sum([len(el)>0 for el in sents]) # don't count empty sentences			  
    return(res)

def show_syllables(s, language="en", country='GB'):
    """Same as count_syllables but puts inserts an n-dash at
       each hyphenation point."""
    h = get_hyphenator(language, country)
    words = word_tokenize(s)
    res = [h.inserted(w) for w in words]
    res = ' '.join(res)
    return(res)

cre = re.compile(r'[\n\r]+')
def count_lines(text):
    """Count the number of lines using the regular expression above
        don't count whitespace-only lines"""
    return len([line for line in cre.split(text) if line.strip()])
