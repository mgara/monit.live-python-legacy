#!/usr/bin/env bash
#prerequisites
virtualenv venv
source venv/bin/activate

#install requirements
pip install -r requirements/local.txt
pip install -r requirements/test.txt
pip install -r requirements.txt

# build
python manage.py compilemessages
python manage.py collectstatic --noinput

# test
coverage run manage.py test
coverage report
coverage xml

# deploy
# TODO
