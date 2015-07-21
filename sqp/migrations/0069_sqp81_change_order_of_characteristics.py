# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        #1
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Theoretical range of the concept bipolar/unipolar' WHERE id = 74;
        """)
        #2
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Extra information or definition' WHERE id = 51;
        """)
       
        #3
        db.execute_many("""
        UPDATE sqp_label SET name = 'More than 3 category scales' WHERE id = 107;
        UPDATE sqp_label SET name = 'Two-category scales' WHERE id = 108;
        UPDATE sqp_label SET name = 'Numerical open-ended answers' WHERE id = 109;
        """)

        #4
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Labels with short text or complete sentences' WHERE id = 38;
        """)
        
        #5
            #1->52 if 1=1
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 52 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 1 and code=1);
        """)
            #52->4
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 4 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 52);
        """)
            #6->8
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 8 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 6);
        """)
        
        
        
        #6
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Maximum possible value' WHERE id = 75;
        """)
        
        
        #8
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Overlap of scale labels and categories' WHERE id = 60;
        """)
        #9
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Scale with only numbers or numbers in boxes' WHERE id = 59;
        """)
        #10
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Request on the show card' WHERE id = 56;
        """) 

    def backwards(self, orm):
        "Write your backwards methods here."
       
        
           
        

    complete_apps = ['sqp']
