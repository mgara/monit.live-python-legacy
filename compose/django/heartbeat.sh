#!/bin/sh
ENV='/root/venv'
APP_DIR='/root/kairos/'
source $ENV/bin/activate
source $APP_DIR/dev.env
cd $APP_DIR

python manage.py  host_heartbeat --host localhost --port 5001
