import os

DEBUG = False
TEMPLATE_DEBUG = False

from local_settings import ADMINS

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_OPTIONS = {"init_command": "SET storage_engine=INNODB"}
DATABASE_HOST = ''             #  Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

#The base path to the project
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

#This is a sample db file with fewer codings for faster tests
TEST_DB_DUMP_FILE   = os.path.join(PROJECT_DIR, "data", "sqp_test_dump.sql")
#This is a file that will be used to dump the production db and import it to a test db
PRODUCTION_DB_FILE = "/tmp/sqp_prod.sql"
#The commands to init south on the imported test db
MANAGE_TEST_PY = "c:\djangoapps\sqp_project\manage_test.py"

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/sqp/webapps/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'
GRAPPELLI_ADMIN_TITLE = 'SQP Admin'



# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
     "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.middleware.http.SetRemoteAddrFromForwardedFor',
    'django.middleware.doc.XViewMiddleware',
#    'django.contrib.csrf.middleware.CsrfMiddleware',
#    'django.middleware.cache.CacheMiddleware',    
#    'sqp.profile_middleware.ProfileMiddleware',
#    'fullhistory.fullhistory.FullHistoryMiddleware',
)
#CACHE_BACKEND = 'file:///home/sqp/django_cache'
#CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

AUTH_PROFILE_MODULE = 'sqp.UserProfile'
AUTH_PROFILE_DEFAULT_CHARACTERISTIC_SET_ID = 3

ROOT_URLCONF = 'sqp_project.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/home/sqp/webapps/django/sqp_project/templates/",
    "/home/sqp/work/sqp/templates/",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.humanize',
    'sqp_project.sqp',
    'sqp_project.calculate',
    'south'
)

HYPHENATION_DIR = "/home/sqp/webapps/django/sqp_project/sqp/hyphenation/"

TAGGER_DIR = "/home/sqp/webapps/django/sqp_project/sqp/"

LOG_FILENAME = '/home/sqp/webapps/django/sqp_project/sqp/sqp_log.txt'

#Make a file called local_settings.py, but DON'T COMMIT IT TO THE SERVER
#This will let you override all settings with your own local settings

from local_settings import *

