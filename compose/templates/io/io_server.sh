#!/bin/sh
ENV='{{mainapp_venv}}'
APP_DIR='{{mainapp_dir}}'
source $ENV/bin/activate
source $APP_DIR/dev.env
cd $APP_DIR

./djangomonitcollector_io/dmc_io.py -B $CELERY_BROKER_URL -H $IO_SERVER -P $IO_PORT
