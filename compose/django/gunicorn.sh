#!/bin/sh
ENV='../../venv/'
APP_DIR='/webapps/kairos'
source $ENV/bin/activate
source $APP_DIR/source_me
cd $APP_DIR

python manage.py collectstatic --noinput
gunicorn config.wsgi -w 4 -b 127.0.0.1:5001 --chdir=.
