# Django settings for xscheduling project.

import os.path
from django.conf import global_settings

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'      # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'xscheduling.db' # Or path to database file if using sqlite3.
DATABASE_USER = ''               # Not used with sqlite3.
DATABASE_PASSWORD = ''           # Not used with sqlite3.
DATABASE_HOST = ''               # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''               # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'site_media') 
APP_MEDIA_ROOT = MEDIA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

SERVE_MEDIA = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = '0vcgot%&tx$b34r4i+au$(x8-(^*2q-^428o=5gkn@68lw@^*-'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'xscheduling.urls'

import os.path
TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',

    'app_media',
    'south',
    'uni_form',
    
    'api_settings',
    'workflowmax',
    'schedule',
    'client',
    'staff',
    'supplier',
    'job',
    'fullcalendar',
)

LOGIN_URL = '/login/'
WORKFLOWMAX_APIKEY = '' #'14C10292983D48CE86E1AA1FE0F8DDFE'
WORKFLOWMAX_ACCOUNTKEY = '' #'0E954F0B52234841BBC64A677C52A77E'

# Google Apps Settings
GAPPS_DOMAIN = 'lawnandhedgecompany.com'
GAPPS_USERNAME = 'admin'
GAPPS_PASSWORD = 'fbetts'

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', 'google_auth.auth.GoogleAppsBackend', )

GOOGLE_APIKEY = 'HJFGHFHFJHJGJHG3927382JHHHI48VY458TY4'
GOOGLE_GEOCODER_KEY = 'ABQIAAAAjE7l2Vf2rzqYeiBc2Km2WhRi_j0U6kJrkFvY4-OX2XYmEAa76BSDtIb-83PiGbAaTOGX2zEorW8V5w'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.debug",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
)

DATE_INPUT_FORMATS = ('%m/%d/%Y',)
TIME_INPUT_FORMATS = ('%H:%M',)
