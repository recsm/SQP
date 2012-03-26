import os


from settings import *

try:
    from local_settings import *
except ImportError, exp:
    pass

TEST_DATA_SQL_FILE = os.path.join(PROJECT_DIR, "data", "sqp_test_dump.sql")

#Overide the database name and any other settings for the test environment here 
DATABASE_NAME = 'sqp_test'            