# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # 4) Characteristic: 49-Respondent instruction: I would like to move it up in the routing as well. It can be placed just before the characteristic 33-Presence of encouragement to answer.
        # 4.1. Move branch from 50 -> 49 to 50 -> 51
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 51 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 50);
        """)
        # 4.2. Move branch from 32 -> 33 to 32 -> 49
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 49 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 32);
        """)
        # 4.3. Move branch from 49 -> 51 to 49 -> 33
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 33 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 49);
        """)

        # 5) Characteristic 51-Extra motivation: I would like to move it up in the routing also. It can be placed just after the characteristic 35-Information about the opinion of other people. This characteristic has a sub characteristic that only pops up when you say a motivation is present: 53-Knowledge provided. If possible I would like to use here to the show  and hide option.
        # 5.1. Move branch from 50 -> 51 to 50 -> 1
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 1 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 50);
        """)
        # 5.2. Move branch from 35 -> 29 to 35 -> 51
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 51 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 35);
        """)
        # 5.3. Move branch from 53 -> 1 to 53 -> 29
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 29 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 53);
        """)

        # 6) Characteristic 50-Interviewer instruction: I would like to move it down in the routing. It can be placed just after the characteristic 83-Interviewer.
        # 6.1. Move branch from 47 -> 50 to 47 -> 1
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 1 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 47);
        """)
        # 6.2. Move branch from 83 -> 82 to 83 -> 50
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 50 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 83);
        """)
        # 6.3. Move branch from 50 -> 1 to 50 -> 82
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 82 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 50);
        """)

        # 7) In characteristic 36-Response scale: I would like to reformulate the names of the options. Change the option 'Categories' to 'More than 3 category scales', the option 'Yes/No answer scale' to 'Two category scales', the option 'Frequencies or amounts' to 'Amounts'
        db.execute_many("""
        UPDATE sqp_label SET name = 'More than 3 category scales' WHERE id = 107;
        UPDATE sqp_label SET name = 'Two category scales' WHERE id = 108;
        UPDATE sqp_label SET name = 'Amounts' WHERE id = 109;
        """)
        
        # 8) Correct the name of the characteristic 75-Number of frequencies to 'Maximum possible amount'
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Maximum possible amount' WHERE id = 75;
        """)

        # 9) Correct the name of the characteristic 38-Labels with short or long text to 'Labels with short text or complete sentences'
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Labels with short text or complete sentences' WHERE id = 38;
        """)

        # 10) Correct the name of the characteristic 51-Extra motivation, information or definition available to 'Extra information or definition'
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Extra information or definition' WHERE id = 51;
        """)

        # 11) Correct the name of the characteristic 60-Overlap of text categories to 'Overlap of labels and categories'
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Overlap of labels and categories' WHERE id = 60;
        """)

        # 12) Correct the name of the characteristic 59-Scale with number or numbers in boxes to 'Scale with only numbers or numbers in boxes'
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Scale with only numbers or numbers in boxes' WHERE id = 59;
        """)

        # 13) Correct the name of the characteristic 56-Question on the show card to 'Request on the show card'
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Request on the show card' WHERE id = 56;
        """)    

    def backwards(self, orm):
        # 13) Correct the name of the characteristic 56-Question on the show card to 'Request on the show card'
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Question on the showcard' WHERE id = 56;
        """)
        
        # 12) Correct the name of the characteristic 59-Scale with number or numbers in boxes to 'Scale with only numbers or numbers in boxes'
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Scale with numbers or numbers in boxes' WHERE id = 59;
        """)
        
        # 11) Correct the name of the characteristic 60-Overlap of text categories to 'Overlap of labels and categories'
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Overlap of text and categories?' WHERE id = 60;
        """)
        
        # 10) Correct the name of the characteristic 51-Extra motivation, information or definition available to 'Extra information or definition'
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Extra motivation, info or definition available?' WHERE id = 51;
        """)
        
        # 9) Correct the name of the characteristic 38-Labels with short or long text to 'Labels with short text or complete sentences'
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Labels with long or short text' WHERE id = 38;
        """)

        # 8) Correct the name of the characteristic 75-Number of frequencies to 'Maximum possible amount'
        db.execute_many("""
        UPDATE sqp_characteristic SET name = 'Number of frequencies' WHERE id = 75;
        """)
        
        # 7) In characteristic 36-Response scale: I would like to reformulate the names of the options. Change the option 'Categories' to 'More than 3 category scales', the option 'Yes/No answer scale' to 'Two category scales', the option 'Frequencies or amounts' to 'Amounts'
        db.execute_many("""
        UPDATE sqp_label SET name = 'Categories' WHERE id = 107;
        UPDATE sqp_label SET name = 'Yes/no answer scale' WHERE id = 108;
        UPDATE sqp_label SET name = 'Frequencies or amounts' WHERE id = 109;
        """)

        # 6) Characteristic 50-Interviewer instruction: I would like to move it down in the routing. It can be placed just after the characteristic 83-Interviewer.
        # 6.3. Move branch from 50 -> 1 to 50 -> 82
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 1 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 50);
        """)
        # 6.2. Move branch from 83 -> 82 to 83 -> 50
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 82 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 83);
        """)
        # 6.1. Move branch from 47 -> 50 to 47 -> 1
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 50 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 47);
        """)
        
        # 5) Characteristic 51-Extra motivation: I would like to move it up in the routing also. It can be placed just after the characteristic 35-Information about the opinion of other people. This characteristic has a sub characteristic that only pops up when you say a motivation is present: 53-Knowledge provided. If possible I would like to use here to the show  and hide option.
        # 5.3. Move branch from 53 -> 1 to 53 -> 29
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 1 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 53);
        """)
        # 5.2. Move branch from 35 -> 29 to 35 -> 51
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 29 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 35);
        """)
        # 5.1. Move branch from 50 -> 51 to 50 -> 1
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 51 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 50);
        """)

        # 4) Characteristic: 49-Respondent instruction: I would like to move it up in the routing as well. It can be placed just before the characteristic 33-Presence of encouragement to answer.
        # 4.3. Move branch from 49 -> 51 to 49 -> 33
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 51 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 49);
        """)
        # 4.2. Move branch from 32 -> 33 to 32 -> 49
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 33 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 32);
        """)
        # 4.1. Move branch from 50 -> 49 to 50 -> 51
        db.execute_many("""
        UPDATE sqp_branch SET to_characteristic_id = 49 WHERE label_id in (SELECT id FROM sqp_label WHERE characteristic_id = 50);
        """)
        

    complete_apps = ['sqp']
