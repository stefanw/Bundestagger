# -*- coding: utf-8 -*-
# Django settings for django default project.

import os.path

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SERVE_MEDIA = DEBUG

SITE_DOMAIN = "http://localhost:8000"

ADMINS = ()

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'NAME': 'bundestagger',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'bundestagger',
        'PASSWORD': 'bundestagger'
    }
}

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

DEFAULT_CHARSET = 'utf-8'

LOCALE = "de_DE.UTF-8"

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'de'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, '..', 'media')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media/'

CSSTIDY_ARGUMENTS = "--template=highest --preserve_css=true --merge_selectors=2"

COMPRESS_JS = {
    'bundes_js': {
        'source_filenames': ('js/jquery.colorPicker.js', 'js/jquery.autocomplete.js','js/annotate.js','js/thickbox.js'),
        'output_filename': 'js/bundes_js.js',
    }
}

COMPRESS_CSS = {
    'bundes_css': {
        'source_filenames': ('css/screen.css',),
        'output_filename': 'css/bundes_css.css',
        'extra_context': {
            'media': 'screen,projection',
        }
    }
}

COMPRESS_VERSION = True

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

INTERNAL_IPS = ('127.0.0.1',)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_openid.consumer.SessionConsumer',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'lazyinclude.middleware.LazyIncludeMiddleware',
)

ROOT_URLCONF = 'bundestagger.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "templates"),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    'django.contrib.messages.context_processors.messages',
    "bundestagger.account.context_processors.openid",
    "bundestagger.account.context_processors.user",
    "bundestagger.account.context_processors.next",
    "bundestagger.account.context_processors.domain",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.messages',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'django.contrib.admin',
    
    'django_openid',
    'tagging',
    'pagination',
    'compress',

    'annotatetext',
    'lazyinclude',
    'improvetext',
    
    'bundestag',
    'bundesstats',
    'bundestagging',
    'helper',
    'account',
    'search',
    'api',    
)
 
CACHE_BACKEND = 'db://bundestagger_cache'
CACHE_TIMEOUT = 7200
CACHED_TYPES = ("text/html",)
GET_CACHE_KEY_MODULE = "helper.utils"

DONT_CACHE_URLS = ("/bundesadmin/","/openid/")
DONT_CACHE_SUFFIXES = (".js", ".jpg", ".css", ".png", ".gif") # for dev mode only

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG
CONTACT_EMAIL = "mail@stefanwehrmeyer.com"
SITE_NAME = "BundesTagger"

TEST_DATABASE_CHARSET = "utf8"
TEST_DATABASE_COLLATION = "utf8_general_ci"

DEFAULT_FROM_EMAIL = "mail@stefanwehrmeyer.com"

SPEECHES_PER_PAGE = 10

IMPROVEMENT_PRIVATE_FEED = "latest"

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass