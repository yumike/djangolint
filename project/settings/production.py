import os

from settings.common import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'project',
    }
}


BROKER_BACKEND = 'redis'
BROKER_HOST = 'localhost'
BROKER_PORT = 6379
BROKER_VHOST = '0'

CELERY_RESULT_BACKEND = 'redis'
CELERY_REDIS_HOST = 'localhost'
CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 0
