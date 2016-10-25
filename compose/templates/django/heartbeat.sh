#!/bin/sh
ENV='{{mainapp_venv}}'
APP_DIR='{{mainapp_dir}}'
source $ENV/bin/activate
source $APP_DIR/dev.env
cd $APP_DIR

python manage.py  host_heartbeat --host localhost --port 5001
