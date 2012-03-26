from django.core.management.base import BaseCommand, CommandError

from sqp_project.calculate.utilities import run_calculation

import csv

class Command(BaseCommand):
    '''
        manage.py calculate conference presentation_is_accepted
    
        to implement, add your calculations to a calculations.py file inside your app
        
        ex) esra/conference/calulations.py
    '''
    
    args = '<appname calculation>'
    help = 'Runs a calculation from an app calulations.py file on all objects in a model'

    def handle(self, *args, **options):
        
        if len(args) != 2:
            raise CommandError('2 arguments were expected and %s were given. Please specify the app name and calulation name as arguments' % len(args))

        appname     = args[0]
        calcname    = args[1]
        
        try:
            exec("from %s.calculations import %s" % (appname, calcname))
            
        except:
            raise CommandError('Could not import the calculation %s from %s/calculations.py' % (calcname, appname))

        try:
            calculation = False
            
            exec("calculation = %s()" % calcname)
            
        except:
            raise CommandError('Error creating calculation instance for %s' % calcname)

        
        run_calculation(calculation, verbose=True)
        
        

            

