#!/bin/sh

source /opt/monit-collector/venv/bin/activate
source /opt/monit-collector/app/source_me
cd /opt/monit-collector/app

python manage.py  host_heartbeat --host localhost --port 5000
