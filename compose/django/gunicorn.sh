#!/bin/sh

source /opt/monit-collector/venv/bin/activate
source /opt/monit-collector/app/source_me
cd /opt/monit-collector/app

python manage.py collectstatic --noinput
gunicorn config.wsgi -w 10 -b 127.0.0.1:5000 --chdir=.
