ADMINS = (
    ('Stefan Wehrmeyer', 'mail@stefanwehrmeyer.com'),
)


#INSTALLED_APPS = (
#    # included
#    'django.contrib.auth',
#    'django.contrib.contenttypes',
#    'django.contrib.sessions',
#    'django.contrib.humanize',
#    'django.contrib.admin',
#    
#    'bundestagger.django_openid',
#    'bundestagger.django_restapi',
#    'bundestagger.bundestag',
#    'bundestagger.bundesstats',
#    'bundestagger.helper',
#    'annotatetext',
#    'bundestagger.account',
#    'bundestagger.debug_toolbar',
#    'bundestagger.pagination',
#    'bundestagger.tagging',
#    'bundestagger.djangodblog',
#    'bundestagger.compress',
#    'bundestagger.improvement',
#    'bundestagger.api',
#    
#    'bundestagger.couchimport',
#)
#
#MIDDLEWARE_CLASSES = (
#    'django.contrib.csrf.middleware.CsrfMiddleware',
#    'django.middleware.common.CommonMiddleware',
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'bundestagger.django_openid.consumer.SessionConsumer',
#    'django.middleware.doc.XViewMiddleware',
#    'bundestagger.helper.middleware.LazyIncludeMiddleware',
##	'bundestagger.debug_toolbar.middleware.DebugToolbarMiddleware',
##	'bundestagger.pagination.middleware.PaginationMiddleware',
#    'bundestagger.djangodblog.middleware.DBLogMiddleware',
#)
#
#DEBUG=False

COUCHDB_HOST = 'http://localhost:5984/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'bk-dasd03riar79nm=asdjgaj*bwc=-ymeit(8a20ad(/&%$whp3goq4dh71t)s'
YAHOO_BOSS_KEY = "Z4lpMw_V34EoNIpGx.9HIrQaIiXG6xVIabDkEAXfHWi6reMIBxuDDh1ASM.wlHVy"
IMPROVEMENT_PRIVATE_FEED = "__private_38hado9no_latest"

#import os
#PROTOCOL_PATH = os.path.join(PROJECT_ROOT, "parser", "data")
#if not PROTOCOL_PATH.endswith("/"):
#    PROTOCOL_PATH += "/"