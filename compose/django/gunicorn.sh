#!/bin/sh

source /opt/monit-collector/venv/collector/bin/activate
source /opt/monit-collector/app/django-monit-collector/source_me
cd /opt/monit-collector/app/django-monit-collector

python manage.py collectstatic --noinput
gunicorn config.wsgi -w 4 -b 127.0.0.1:5000 --chdir=.
