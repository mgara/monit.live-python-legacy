# -*- coding: utf-8 -*-
'''
Local settings

- Run in Debug mode
- Use console backend for emails
- Add Django Debug Toolbar
- Add django-extensions as app
'''

from .common import *  # noqa
import os


# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DJANGO_DEBUG', default=True)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env("DJANGO_SECRET_KEY",
                 default='%6nue!!u11n47bo7_bkr06-ch_n38@60@92j9r&4li06!ugp*h')

# Mail settings
# ------------------------------------------------------------------------------
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025


# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

# django-debug-toolbar
# ------------------------------------------------------------------------------
#MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
#INSTALLED_APPS += ('debug_toolbar', )

INTERNAL_IPS = ('127.0.0.1', '10.0.2.2',)

#DEBUG_TOOLBAR_CONFIG = {
#    'DISABLE_PANELS': [
#        'debug_toolbar.panels.redirects.RedirectsPanel',
#    ],
#    'SHOW_TEMPLATE_CONTEXT': True,
#}

# django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += ('django_extensions', )

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# CELERY
# In development, all tasks will be executed locally by blocking until the
# task returns
CELERY_ALWAYS_EAGER = True
# END CELERY

# OPBEAT
#INSTALLED_APPS += (
#    'opbeat.contrib.django',
#)

#OPBEAT = {
#    'ORGANIZATION_ID': 'e2cf9ccf35b84522abd79e2ed4f4bddf',
#    'APP_ID': 'f3a5eecfcb',
#    'SECRET_TOKEN': '5b54a925063c5cc3bcde9ef9a2db0e6bb76c1615',
#}

#MIDDLEWARE_CLASSES += ('opbeat.contrib.django.middleware.OpbeatAPMMiddleware',)

# END OPBEAT

# Your local stuff: Below this line define 3rd party library settings

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/kairos/kairos.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}
