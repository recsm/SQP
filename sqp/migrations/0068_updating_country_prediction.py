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
        """Sets question country or USA to prediction country"""

        questions=sqp_models.Question.objects.filter(country__available=True)
        for q in questions:
            q.country_prediction=q.country
            q.save_through()
        
        default_country=sqp_models.Country.objects.get(iso='XX')
        questions=sqp_models.Question.objects.filter(country__available=False).update(country_prediction=default_country)
        

    def backwards(self, orm):
        "Write your backwards methods here."

    complete_apps = ['sqp']
