# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):


    def forwards(self, orm):
        # Rename Item.long_name to Item.concept
        db.rename_column('sqp_item', 'long_name', 'concept')


    def backwards(self, orm):
        # Rename Item.concept to Item.long_name
        db.rename_column('sqp_item', 'concept', 'long_name')