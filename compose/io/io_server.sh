#!/bin/sh

source /opt/monit-collector/dmcio_venv/bin/activate
source /opt/monit-collector/app/source_me
cd /opt/monit-collector/app

./djangomonitcollector_io/dmc_io.py -B $CELERY_BROKER_URL -H $IO_SERVER -P $IO_PORT
