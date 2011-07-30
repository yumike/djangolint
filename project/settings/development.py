import os

from settings.common import *


DEBUG = True
TEMPLATE_DEBUG = DEBUG


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'sqlite.db'),
    }
}


INSTALLED_APPS +=(
    'djkombu',
)


BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
CELERY_RESULTS_BACKEND = "djkombu.transport.DatabaseTransport"
