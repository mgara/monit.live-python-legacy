#!/bin/sh
ENV='{{mainapp_venv}}'
APP_DIR='{{mainapp_dir}}'
source $ENV/bin/activate
source $APP_DIR/source_me
cd $APP_DIR

python manage.py collectstatic --noinput
gunicorn config.wsgi -w 4 -b 127.0.0.1:5001 --chdir=.
