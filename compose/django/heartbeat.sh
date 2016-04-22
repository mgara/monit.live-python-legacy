#!/bin/sh

source /opt/monit-collector/venv/collector/bin/activate
source /opt/monit-collector/app/django-monit-collector/source_me
cd /opt/monit-collector/app/django-monit-collector

python manage.py  host_heartbeat --host localhost --port 5000
