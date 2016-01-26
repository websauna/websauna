============================================
Deploying Websauna application to production
============================================

Introduction
============

Websauna applications can be run on any webserver supporting Python's :term:`WSGI` protocol. This covers pretty much any web server: Apache, Nginx, IIS (`see full list <http://wsgi.readthedocs.org/en/latest/servers.html>`_). Websauna assumes a developer has full admin control of server. Shared hosting is no go, because in these kind of environments it's often impossible to run Celery and other background workers. Thus, a full server is needed. Luckily Linux virtual machines go almost free nowadays.

Setting up a full server from scratch to a fully functioning and secured state is cumbersome tasks. Websauna automatizes this for you.

* Have your Websauna application source code committed to a Git repository, private or public

* Take any pristine Linux server with SSH access

* Point Websauna's :term:`Ansible` playbook to this server

* websauna.ansible playbook takes a connection to the server and runs :term:`playbook` to set up the stack for you

* 30 minutes later your site is running in production, with high security and high performance setup

.. note ::

    The current playbook is only tested with Ubuntu Linux 14.04. Making it to work other Linux distributions may require minor modifications.
