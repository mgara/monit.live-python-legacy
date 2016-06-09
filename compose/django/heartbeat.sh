#!/bin/sh
ENV='/webapps/envs/kairos'
APP_DIR='/webapps/kairos'
source $ENV/bin/activate
source $APP_DIR/source_me
cd $APP_DIR

python manage.py  host_heartbeat --host localhost --port 5001
