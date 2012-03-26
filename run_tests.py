import unittest
import sys
import os
import subprocess
import MySQLdb

###Usage
#
# ./python run_tests.py
# 
#  Optional arugument -r or --reset-db to fully reset the database from the file in the repository
#
#  Optional arugument -p or --copy-production-db to copy the production database and run the tests

RESET_FROM_FILE = 1
RESET_FROM_PRODUCTION_DB = 2

def main():
    
    if "--reset-db" in sys.argv or "-r" in sys.argv:
        print "Resetting Database from file"
        reset_db = RESET_FROM_FILE
    elif "--copy-production-db" in sys.argv or "-p" in sys.argv:
        print "Beginning dump of production database"
        reset_db = RESET_FROM_PRODUCTION_DB
   
    else:
        print "Skipping Database Reset. Use -r to run with reset" 
        reset_db = None
        
    migrate = "--migrate" in sys.argv or "-m" in sys.argv
    init_south = "--init_south" in sys.argv or "-i" in sys.argv
         
    setup_environment(reset_database=reset_db, migrate=migrate, init_south=init_south)
    
    print " "
    print "######################################################################"
    print " "
    print "Running sqp/tests.py"
    #Start with our basic tests
    test_manager = TestManager()
    from sqp.tests import test_order
    for test_case in test_order:
        test_manager.add_test(test_case)
    test_manager.run_tests()
    
    
    
 

def setup_environment(reset_database=None, migrate=False, init_south=False):
    #Setup our path correctly
    sys.path.append(os.path.dirname(__file__).replace('sqp_project', ''))
    
    #The order of the below imports is important for everything to work ok    
    #Get Django to setup the base environment
    from django.core.management import setup_environ
    import settings_test
    setup_environ(settings_test)
    #Modify the environent to be a test environment
    from django.test.utils import setup_test_environment
    setup_test_environment()
    #Verify we are using the test database
    from django.conf import settings
    
    if settings.DATABASE_NAME != 'sqp_test':
        print "The database is not sqp_test. Exiting. Please change settings.DATABASE_NAME in settings_test.py to sqp_test to continue"

    if reset_database is not None: 
        connection = MySQLdb.connect(user=settings.DATABASE_USER,
                              passwd=settings.DATABASE_PASSWORD)
        
        cursor=connection.cursor()
        try:
            print "Trying to drop old sqp_test"
            cursor.execute('DROP DATABASE IF EXISTS sqp_test ;');
            print "sqp_test dropped"
        except:
            print "Database sqp_test not dropped (error or doesn't exist)"
        
        print "Recreating sqp_test db"    
        cursor.execute('CREATE DATABASE sqp_test ;');
        connection.close()
        
        if reset_database == RESET_FROM_FILE:
            file = settings.TEST_DATA_SQL_FILE
        
            #Read in the database dump file into our test db
            #Prepare the dump by deleting codings and completions for any question id above 100
            #DELETE FROM `sqp_completion` WHERE `question_id` > 100
            #DELETE FROM `sqp_coding` WHERE `question_id` > 100
            #mysqldump and save in data directory as sqp_test_dump.sql
            #This assumes that the database sqp_test already exists
            print "Beginning import of test sql dump %s " % settings.TEST_DATA_SQL_FILE
            
        elif reset_database == RESET_FROM_PRODUCTION_DB:
            print "Dumping sqp_prod to file %s" %  settings.PRODUCTION_DB_FILE

            #Dump the production database
            subprocess.call(['mysqldump -u sqp --password=%s -h localhost sqp_prod > %s' \
                              % (settings.PRODUCTION_DB_PASSWORD, settings.PRODUCTION_DB_FILE)],
                                                                                shell=True)
            
            print "Beginning import of production sql dump %s" %  settings.PRODUCTION_DB_FILE
            file = settings.PRODUCTION_DB_FILE
            
        subprocess.call(['mysql -u %s --password=%s -h localhost %s < %s'   % (settings.DATABASE_USER, 
                                                                               settings.DATABASE_PASSWORD,
                                                                               settings.DATABASE_NAME,
                                                                               file)],
                                                                               shell=True)
    if init_south:
        print "Initializing South"
        print "%s syncdb" % settings.MANAGE_TEST_PY
        subprocess.call(["%s syncdb" % settings.MANAGE_TEST_PY], shell=True)
        subprocess.call(["%s migrate sqp 0001 --fake" % settings.MANAGE_TEST_PY], shell=True)
        
    if migrate:
        print "Running South Migrations"
        print settings.MANAGE_TEST_PY + " migrate sqp"
        subprocess.call([settings.MANAGE_TEST_PY + " migrate sqp"],
                         shell=True)

class TestManager:
    suite       = None
    
    def __init__(self):
        self.suite = unittest.TestSuite()
         
    def add_tests_from_module(self, module_name):
        self.suite.addTests(unittest.TestLoader().loadTestsFromName(module_name))
        
    def add_test(self, test_case):
        self.suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test_case))
    
    def run_tests(self):
        unittest.TextTestRunner(verbosity=2).run(self.suite)

if __name__ == "__main__":
    main()
    