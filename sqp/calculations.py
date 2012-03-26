import json
import csv
import sys
import MySQLdb
from decimal import *


#This file is imported from conference.models.py at the very bottom so all the signals are managed correctly
from django.contrib.auth.models import User

from django.conf import settings
#from sqp_project.calculate.utilities import run_calculation
from django.db.models.signals import m2m_changed, post_save, post_delete

#from sqp_project.sqp.stats import lmean, lmode, lvariation, lsterr, lstdev

from sqp_project.calculate.utilities import Calculation
from sqp_project.sqp.models import Question, Coding, Item, UserProfile


    

#Calculate if a coding has been orphaned
class OrphanedCodings(Calculation):
    #The model related to this calculation, an object from this model will be passed to calculate
    model = Question
    
    #This calculation actually marks the codings driectly, so here we set field to false
    #since we aren't expecting our return value to be autosaved
    save_to_field = False
    csvfile = False
    writer  = False
    
    def init(self):
        #create a log file of our changes
        self.csvfile = open('orphaned.csv', "wb")
        fieldnames = ['question_id', 'question', 'coder', 'total_valid', 'total_orphaned', ]
        self.writer = csv.DictWriter(self.csvfile, fieldnames, restval = ".", #NA
                    extrasaction = 'ignore',
                    dialect='excel', delimiter=';') 
        self.writer.writerow(dict([(fnam, fnam) for fnam in fieldnames])) # header
        
        print "---------------------------------------------------------"
        print "---------   See ./orphaned.csv for mode details ---------"
        print "---------------------------------------------------------"
        
    def close(self):
        self.csvfile.close()
        
    def calculate(self, object):
        question = object
        #get a unique list of coders who have coded a question and loop over it
        for coder in User.objects.filter(coding__question = question).distinct():
           
            #for each coder get all of the codings
            question_valid_characteristics = set([])
            orphaned = set([])
            
            for branch in question.iter_branches(user=coder,charset=3):
                if branch:
                    #Add all possible valid characteristics to a list
                    question_valid_characteristics.add(branch.label.characteristic)    
             
            #load all codes made by this coder and for this question
            #if they are not valid we mark them as orpaned
            for code in Coding.objects.filter(user=coder, question=question):
                if code.characteristic in question_valid_characteristics:
                    code.calc_is_orphaned = False
                else :
                    code.calc_is_orphaned = True
                    orphaned.add(code.characteristic.short_name)
                code.save()
                
            sys.stdout.write(".")    
            
            rowdict = {'question_id'      : question.id,
                       'question'         : question,
                       'coder'            : coder,
                       'total_valid'      : len(question_valid_characteristics),
                       'total_orphaned'   : len(orphaned),
                                                 
                       }
            self.writer.writerow(rowdict)
          
            
class CollectItemCodings(Calculation):
    """
        For each coding, we gather the related codings + frequencies  
    """
    
    #The model related to this calculation, an object from this model will be passed to calculate
    #This is also the model which will have its objects iterated over
    model  = Item
    
    #We will take care of saving this ourself, so no save_to_field
    save_to_field = False
    
    connection  = False
    cursor      = False
    
    #This gets called only once before all the calculations are run
    #If you want to open a log file, it may be opened here
    def init(self):
        self.connection = MySQLdb.connect(user=settings.DATABASE_USER,
                              passwd=settings.DATABASE_PASSWORD,
                              db=settings.DATABASE_NAME )

        self.cursor=self.connection.cursor(MySQLdb.cursors.DictCursor)

    #This gets called only once after all the calculations are run
    #If you want to close a log file, it may be closed here
    def close(self):
        self.connection.close()
    
    
    #The actual calculation
    #For each item, we will get all related codings
    #The values will then be grouped, and ordered by the number of values in each group
    #At the same time we will make a calculation of the deviation for each coding from 
    #the related choices made by other coders
    def calculate(self, object):
        #The object here is an Item, so we rename it for readability
        item = object
        
        print u"Updating %s" % item
        
        #Get all valid codings for this item:
        
        sql = "SELECT c.* , i.admin, i.name AS item, \
               ch.short_name AS characteristic \
               FROM `sqp_coding` AS c \
               JOIN sqp_question AS q ON q.id = c.question_id \
               JOIN sqp_item AS i ON i.id = q.item_id \
               JOIN sqp_characteristic AS ch ON ch.id = c.characteristic_id \
               WHERE i.id = %s \
               AND c.invalidated = 0" % item.id
        
        
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        
        char_totals = {}
        coding_ids = {}
        char_values = {}
        
        for row in results:
            char        = row['characteristic']
            choice      = row['choice']
            choice_id   = row['id']
            
            if char not in char_totals:
                char_totals[char] = {}
                char_values[char] = []
                coding_ids[char]  = []
            
            if choice not in char_totals[char]:
                char_totals[char][choice] = 1
            else :
                char_totals[char][choice] += 1
            
            coding_ids[char].append(unicode(choice_id))
            char_values[char].append(float(choice))
            
            
        for char in coding_ids:
            
            #If there are related choices, we do some cool calculations
            if len(char_values[char]) > 1:
                                
                item.calc_related_choices = json.dumps(char_totals[char])
                #item.calc_mean            = round(lmean(char_values[char]), 5)
                #maxfreq, item.calc_mode   = lmode(char_values[char])
                #item.calc_sterr           = round(lsterr(char_values[char]), 5)
                #item.calc_stdev           = round(lstdev(char_values[char]), 5)
                item.save()
           
    
    
    
def deviance(choice, distribution):
  """
    #choice is a value
    #choice should be of the same type as distribution.keys()
   
    #distribution is a dict showing how many times each choice has been
    #chosen. Only choices that were chosen at least once are included!
    #Keys should be of the same type as choice
    #Values should be int or float
    # As a rule of thumb, chidf > 2 means that it is deviant.
    #Example:
   
    >>>distribution = {'1':2, '2':3, '3':15}
    >>>choice = '2'
   
    >>>deviance(choice, distribution)
    2.408333

   
    >>>choice = '1'
    >>>deviance(choice, distribution)
    4.05
   
    >>>choice = '3'
    >>>deviance(choice, distribution)
    0.04166667
  """
  # check that choice in distribution.keys() if not raise exception or return Nothing

  if len(distribution) == 1:
      return float(0);  
  
  if choice not in distribution:
      return 999; #error
  
    
  total = sum(distribution.itervalues())
  
  pdist = dict((k, float(v)/float(total)) for k,v in distribution.items())
  expected = float(pdist[choice])
  
  # Check that expected not equals 0
  chisq = (1.0 - expected)**2 / expected
  df = float(len(distribution) - 1)
 
  chidf = chisq/df
 
  # If a boolean is needed as return value, take 2 as cutoff:
  # return (chidf > 2.0)
 
  return chidf




class CodingQuality(Calculation):
    """
        For each coding, we gather the related deviance and frequency, mean, mode, and sterr
        This must be run AFTER collect_item_codings
    """
   
    #The model related to this calculation, an object from this model will be passed to calculate
    #This is also the model which will have its objects iterated over
    model  = Coding
    
    #We will take care of saving this ourself, so no save_to_field
    save_to_field = False
    
    def calculate(self, object):
        coding = object
        print "%s" % coding.id 
        
        #Don't process invalidated codes
        if coding.invalidated:
            return
                
        codings = json.loads(coding.calc_related_choices)
        #Invalidated choices do not include any related choiced
        if len(codings) != 0:
            
            dev = round(deviance(coding.choice, codings), 3) * 1
            coding.calc_choice_deviance  = dev
            coding.calc_choice_frequency = codings[coding.choice]
            coding.save()
            
            
class CreateProfiles(Calculation):
    """For each user we create a profile 
       Usage: $ python manage.py calculate sqp CreateProfiles
    """
   
    #The model related to this calculation, an object from this model will be passed to calculate
    #This is also the model which will have its objects iterated over
    model  = User
    
    #We will take care of saving this ourself, so no save_to_field
    save_to_field = False
    
    def calculate(self, object):
        user = object
        UserProfile.create_profile_for_user(user)
           
            
    
    
    