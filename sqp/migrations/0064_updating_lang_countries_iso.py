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
