monit collector v16.05-1
^^^^^^^^^^^^^^^^^^^^^^^^

Django application for collecting monit metrics, host data management and host alerts management

LICENSE: BSD

Developpement Settings
----------------------

Check cookie-cutter django application settings_.

.. _settings: http://cookiecutter-django.readthedocs.org/en/latest/settings.html

Installation
^^^^^^^^^^^^

.. note::  Installation steps are meant for CentOS 7.

Requirements:

    * nginx
    * rabbitmq
    * postgresql



Installing requirements
-----------------------

Many Packages requires EPEL Repository

1. Installing **epel** repository:

Download the epel rpm package and install it ::

    yum install http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-6.noarch.rpm

2. Installing **Postgresql**

Postgrsql can be installed from here ::

    yum install http://yum.postgresql.org/9.5/redhat/rhel-7-x86_64/pgdg-centos95-9.5-2.noarch.rpm

* Postgresql Configuration ::

    /usr/pgsql-9.5/bin/postgresql95-setup initdb  #initialise database
    systemctl start postgresql-9.5  # Start the database
    su postgres # connect to postgres bash session

In postgres bash session run the psql command to enter the postgresql console: ::

    psql

In the psql invite:
* Create USER/ROLE: ::

    CREATE ROLE kokoro PASSWORD 'md535f5a74e5d624bbea732fd9018b36023' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;
    ALTER USER postgres with password 'WdOKanaoF';

* Create DATABASE:

This command will create a database from PostgreSQL shell prompt, but you should have appropriate privilege to create database. By default, the new database will be created by cloning the standard system database template1. ::

    CREATE DATABASE monit_collector_production;

To exit the invite use: ::

   \q

* Configuring User permissions :

Edit the file **pg_hba.conf**: ::

    vim  /var/lib/pgsql/9.5/data/pg_hba.conf


edit local user to **md5** auth

* Restart the postgresql Service: ::

    systemctl restart postgresql-9.5


3. Installing **RabbitMQ**: ::

     yum install https://www.rabbitmq.com/releases/rabbitmq-server/v3.6.1/rabbitmq-server-3.6.1-1.noarch.rpm
     systemctl start rabbitmq-server
     rabbitmqctl add_user dmc va2root
     rabbitmqctl set_permissions -p / dmc ".*" ".*" ".*"

     # You really don't want to keep the default rabbitmq user:
     rabbitmqctl delete_user guest

*  Optional you can enable the rabbitmq Management module: ::

     rabbitmq-plugins enable rabbitmq_management
     rabbitmqctl set_user_tags dmc administrator

*  For more info check RabbitMQ official documentation_

.. _documentation: https://www.rabbitmq.com/man/rabbitmqctl.1.man.html

Installing the monit-collector rpm:
-----------------------------------

To import first data ::

    $ python manage.py dataload fixture.json

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.


Development:
^^^^^^^^^^^^

Test coverage
-------------

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run manage.py test
    $ coverage html
    $ open htmlcov/index.html
