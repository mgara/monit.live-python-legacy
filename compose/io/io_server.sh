#!/bin/sh
source /root/io_venv/bin/activate
source /root/kairos/dev.env
cd /root/kairos/

./djangomonitcollector_io/dmc_io.py -B $CELERY_BROKER_URL -H $IO_SERVER -P $IO_PORT
