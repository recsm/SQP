#!/usr/local/bin/python2.5
from django.core.management import execute_manager
import sys
import os

sys.path.append('/home/sqp/webapps/django/sqp')
sys.path.append('/home/daob/work')
os.environ['DJANGO_SETTINGS_MODULE'] = 'sqp_project.settings_test'

try:
    import settings_test # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings_test)
