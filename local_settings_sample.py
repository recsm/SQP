
ADMINS = (('Name', 'name@example.com'),)

DATABASE_NAME     = 'sqp'
DATABASE_USER     = 'dbuser'
DATABASE_PASSWORD = 'dbpass'


PRODUCTION_DB_PASSWORD = 'dbpass'


MEDIA_ROOT = '/srv/projects/sqp_project/media/'

LOG_FILENAME = '/srv/projects/sqp_project/local/sqp_log.txt'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/srv/projects/sqp_project/templates/",
)

DEBUG = True
TEMPLATE_DEBUG = True

#CACHE_BACKEND = 'file:///srv/development/sqp_project/local/cache'
#CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

#The commands to init south on the imported test db
MANAGE_TEST_PY       = "/srv/projects/sqp_project/python /srv/sqp_project/manage_test.py"
PYTHON_PATH          = "/srv/projects/sqp_project/python" 
MANAGE_PY            = "/srv/projects/sqp_project/manage.py"
