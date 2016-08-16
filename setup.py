from distutils.core import setup

setup(
    name='django-monit-collector',
    version='0.9b',
    packages=['docs', 'config', 'config.settings', 'djangomonitcollector', 'djangomonitcollector.ui',
              'djangomonitcollector.ui.migrations', 'djangomonitcollector.ui.templatetags',
              'djangomonitcollector.users', 'djangomonitcollector.users.tests',
              'djangomonitcollector.users.migrations', 'djangomonitcollector.contrib',
              'djangomonitcollector.contrib.sites', 'djangomonitcollector.contrib.sites.migrations',
              'djangomonitcollector.taskapp', 'djangomonitcollector.datacollector',
              'djangomonitcollector.datacollector.lib', 'djangomonitcollector.datacollector.tests',
              'djangomonitcollector.datacollector.models', 'djangomonitcollector.datacollector.migrations',
              'djangomonitcollector.notificationsystem', 'djangomonitcollector.notificationsystem.lib',
              'djangomonitcollector.notificationsystem.management',
              'djangomonitcollector.notificationsystem.management.commands',
              'djangomonitcollector.notificationsystem.migrations'],
    url='',
    license='',
    author='Vantrix Platform Team',
    author_email='platform@vantrix.com',
    description=''
)
