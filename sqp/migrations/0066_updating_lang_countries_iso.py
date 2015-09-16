# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
import codecs

from django.conf import settings
from sqp import models as sqp_models

class Migration(DataMigration):

    def forwards(self, orm):
        """Updates the list of countries and languages"""
        noCountry=sqp_models.Country(iso="XX", iso_three="XXX",name="No country selected", available=True)
        noCountry.save()
        #Updating country source SC, repeated iso
        countryNew=sqp_models.Country(iso="SX", iso_three="",name="SOURCE SC")
        countryNew.save()
        questions=sqp_models.Question.objects.filter(country="SS")
        for q in questions:
            q.country=countryNew
            q.save_through()
        assig=sqp_models.QuestionBulkAssignments.objects.filter(country="SS")
        for a in assig:
            a.country=countryNew
            a.save_through()
        country=sqp_models.Country.objects.get(iso="SS")
        country.delete()
        
        Q_BASE_DIR  = settings.PROJECT_DIR + '/data/available_lang_countries/'
        file_name ='countries_iso.txt'

         #utf-8-sig to get rid of the utf-8 BOM /ufeff
         #http://stackoverflow.com/questions/9228202/tokenizing-unicode-using-nltk
        input_file = codecs.open(Q_BASE_DIR + file_name, "r", "utf-8-sig")

        for line in input_file:
            line=line.replace('\n','') 
            codes=line.split('\t') #codes[0] country codes[1] iso codes[2] iso3
            try:
                country = sqp_models.Country.objects.get(iso=codes[1])
            except sqp_models.Country.DoesNotExist:
                country=sqp_models.Country(iso=codes[1], iso_three=codes[2],name=codes[0])
                country.save()
        
        #Change label of Taiwan
        country = sqp_models.Country.objects.get(iso="TW")
        country.name="Taiwan"
        country.save()
        
        file_name ='languages_iso.txt'

        input_file = codecs.open(Q_BASE_DIR + file_name, "r", "utf-8-sig")

        for line in input_file:
            line=line.replace('\n','') 
            codes=line.split('\t') #codes[0] language codes[1] iso2 codes[2] iso (alpha3)
            try:
                language = sqp_models.Language.objects.get(iso2=codes[1])
            except sqp_models.Language.DoesNotExist:
                language=sqp_models.Language(iso=codes[2], iso2=codes[1], name=codes[0])
                language.save()

       

    def backwards(self, orm):
        "Write your backwards methods here."



    complete_apps = ['sqp']
