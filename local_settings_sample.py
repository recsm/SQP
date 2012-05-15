
ADMINS = (('Name', 'name@example.com'),)

DATABASE_NAME     = 'sqp'
DATABASE_USER     = 'root'
DATABASE_PASSWORD = 'ruglocat'


MEDIA_ROOT = '/tdev/projects/sqp_project/media/'

LOG_FILENAME = '/tdev/projects/sqp_project/local/sqp_log.txt'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/tdev/projects/sqp_project/templates/",
)

DEBUG = True
TEMPLATE_DEBUG = True

#CACHE_BACKEND = 'file:///tdev/development/sqp_project/local/cache'
#CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

#The commands to init south on the imported test db
MANAGE_TEST_PY       = "/tdev/projects/sqp_project/python /tdev/sqp_project/manage_test.py"
PYTHON_PATH          = "/tdev/projects/sqp_project/python" 
MANAGE_PY            = "/tdev/projects/sqp_project/manage.py"
