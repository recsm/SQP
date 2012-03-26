#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import forms

from sqp_project.sqp import nlp_tools
from sqp_project.sqp.tagger import count_nouns, tagger_dict

def rfa_num_sentences(question, characteristic):
    "Suggestion for number of sentences in Request for an Answer (RFA)."
    return nlp_tools.count_sentences(question.rfa_text, lan=question.language.iso), None

def int_num_sentences(question, characteristic):
    "Suggestion for number of sentences in introduction."
    return nlp_tools.count_sentences(question.introduction_text, lan=question.language.iso), None

def ans_num_sentences(question, characteristic):
    "Suggestion for number of sentences in answer categories."
    return nlp_tools.count_sentences(question.answer_text, lan=question.language.iso), None

def rfa_num_words(question, characteristic):
    "Suggestion for number of words in Request for an Answer (RFA)."
    return nlp_tools.count_words(question.rfa_text), None

def int_num_words(question, characteristic):
    "Suggestion for number of words in introduction."
    return nlp_tools.count_words(question.introduction_text), None

def ans_num_words(question, characteristic):
    "Suggestion for number of words in answer categories."
    return nlp_tools.count_words(question.answer_text), None

def rfa_num_syllables(question, characteristic):
    "Suggestion for number of syllables in Request for an Answer (RFA)."
    return nlp_tools.count_syllables(question.rfa_text,
                                     language = question.language.iso2,
                                     country = question.country.iso)

def int_num_syllables(question, characteristic):
    "Suggestion for number of syllables in introduction."
    return nlp_tools.count_syllables(question.introduction_text,
                                     language = question.language.iso2, 
                                     country = question.country.iso) 
          

def ans_num_syllables(question, characteristic):
    "Suggestion for number of syllables in answer categories."
    return nlp_tools.count_syllables(question.answer_text, 
                         language = question.language.iso2,
                         country = question.country.iso)

def rfa_num_nouns(question, characteristic):
    "Suggestion for number of nouns in Request for an Answer (RFA)."
    return count_nouns(question.rfa_text, question.language.iso2)

def int_num_nouns(question, characteristic):
    "Suggestion for number of nouns in introduction."
    return count_nouns(question.introduction_text, question.language.iso2)

def ans_num_nouns(question, characteristic):
    "Suggestion for number of nouns in answer categories."
    return count_nouns(question.answer_text, question.language.iso2)

def ncategories(question, characteristic):
    "Suggestion for number of categories"
    return nlp_tools.count_lines(question.answer_text), None

def introduction_available(question, characteristic):
    return 1*(question.introduction_text.strip()!=''), None
  
