===================================
Playbook deployment characteristics
===================================

.. contents:: :local:

Purpose
=======

This is an Ansible playbook for automatically deploying a single server Websauna website from a git repository for Ubuntu 14.04 Linux. It allows you to do deploy your Websauna application to a fresh server, where you just received SSH credentials, within 30 minutes. Alternatively you can gracefully upgrade any existing running site.

.. note ::

    The current version of the playbook is designed for a single server setup. It is, however, easy to extend to cover groups of different servers.

Installed software
==================

Automatic installation sets up

* :term:`PostgreSQL`

* :term:`Nginx`

* :term:`uWSGI`

* :term:`Celery`

* :term:`Postfix`

* Email out via :term:`Mandrill`

* :term:`Supervisor` startup scripts

Database migration and hot deploy aware
=======================================

Playbook runs migrations safely: Run database migrations first and then update codebase with compatible model files. This allows graceful deploys and avoids breaking any running sites.

Filesystem Hierarchy Standard layout
====================================

The application is deployed in the folder ``/srv/pyramid/yoursitename`` per Filesystem Hierarchy Standard.

Default firewalls
=================

A Linux firewall is set up to allow only inbound SSH, HTTP, HTTPS. This for the cases where any process would accidentally bind itself to public Internet facing IP addresses.

No private keys leaked
======================

All communication happens over SSH agent. No private keys are placed on a server in any point.

Privilege separation
====================

The deployed UNIX processes run under corresponding user accounts. This reduces the risk of a compromised data in the case any of the processes has a remote exploit, like Heartbleed vulnerability in the past.


* Websauna application files and uWSGI processes are deployment under a normal UNIX user ``wsgi``

* Nginx runs under UNIX user ``www-data``.

* uWSGI, Celery runs under user ``wsgi``.

* PostgreSQL runs under user ``postgres``.

* Redis runs under user ``redis``.

* Postfix runs under user ``postfix``.

* ``/srv/pyramid/myapp`` is writable and readable by ``wsgi`` only.
