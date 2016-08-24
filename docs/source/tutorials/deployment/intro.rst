==============================================
Deploying a Websauna application to production
==============================================

.. contents:: :local:

Introduction
============

Websauna applications run on any webserver supporting Python's :term:`WSGI` protocol. All popular web servers support this: Apache, Nginx, IIS and others (`see full list <http://wsgi.readthedocs.org/en/latest/servers.html>`_).

Websauna is geared towards custom business applications and assumes the application team has full control over a server. A :term:`shared hosting` is possible, but problematic, because in these kind of environments it's often challenging to install required software packages or run background workers. Thus, a full server is recommended for production installations unless you have considerable Python hosting experience. Luckily Linux virtual machines go almost free nowadays. See :ref:`hosting providers` for suggestions.

Ansible playbook automatisation
===============================

Websauna provides an automated server deployment using :term:`Ansible` tool.

.. note ::

    **Why ansible?**

    Ansible is a popular deployment automatisation tool. Setting up a functional web server, especially when security is concerned, is a difficult and cumbersome task. Doing tasks by hand may take a day from an advanced sysadmin. Doing your first Linux server setup may take days.

    Websauna's Ansible playbooks brings the essence of a well configured Python web server to an automated process.

    * Commit your source code to a :term:`Git` version control

    * Playbook sets up a server and deploys your application from Git

    The scripted Ansible deployments, playbooks, use linear scripting and are easy to understand even for sysadmin people with no programming background. Furthermore Ansible is written in Python and uses the same Jinja 2 template language as Websauna itself.

People with considerable sysadmin experience or custom deployment requirements are still free to do their own thing. Deploying Websauna is not different from deploying any WSGI application (Pyramid, Flask, Django). Even if you are doing this you can gain insight from default playbook, as playbooks are easy to read and understand for humans too.

How does Websauna's playbook work
---------------------------------

The playbook is distributed as a separate `websauna.ansible git repository clone <http://github.com/websauna/websauna.ansible>`_.

* Have your application source code committed to a Git repository, private or public

* Take any pristine Linux server with :term:`SSH` access

* Point Websauna's :term:`Ansible` playbook to this server

* The playbook takes a SSH connection to the server and runs :term:`playbook` to set up the stack for you

* 30-60 minutes later your site is running in production, with sane security and performance defaults

* Playbook can perform update for the existing site by pulling in the new version of source code, running database migrations and gracefully restarting all services.

Deployment process
==================

.. image :: ../images/deployment-model.png
    :width: 640px


Websauna follows a common *development, testing, staging, production* deployment process defining how new application features are developed and deployed.

* Websauna application scaffold and configuration files support this model

* Websauna Ansible playbook supports this model

To work with this model you need at least one developer who knows how to use :term:`Git` version control and a server where you will run your website.

* The model emphasises the fact you have always a working source code state in a version control and you can take a step back if something fails.

* A developer or developers run Websauna on their own computer for the development. They edit the source code files, the development web server automatically restarts itself and a developer refresh their web browser to see changes. Alternatively developers follow test-driven-development (:term:`TDD`) model where each step of source code is written in conjugation with a corresponding test.

* They push the updated source code to a Git version control.

* To make sure the changes did not break any prior features, :ref:`an automated test suite <testing>` **may be** run. Developers add new automated tests to cover new features they add.

* The changes are merged to the master Git branch which is the one going to be deployed on a production server.

* Before deploying on a production server the changes **may be** previewed in a private :term:`staging` environment.

* After all stakeholders are happy with the changes the production server is updated by a playbook. Playbook fetches new source code from the git repository master branch, runs database migration scripts and gracefully restarts the web servers so that website visitors do not see any interruption.

.. note ::

    You do not need to run a staging server or have automated tests for your application. This is highly recommend though if the application bears any business value, as testing and staging process captures errors before they land on a live website.

Read `Deployment environment in Wikipedia <https://en.wikipedia.org/wiki/Deployment_environment#Development>`_ for more background.

Single server deployment example
================================

.. image :: ../images/deployment.png
    :width: 640px


Above is an example diagram of a Websauna deployment on a single server. One Linux server can run the full software stack needed to run a Websauna application in a production. This is what the unmodified Ansible playbook script in this chapter will produce for you.

* :term:`Nginx` terminates HTTP, HTTPS, WS (WebSocket) and WSS (secure WebSocket) traffic, does local outbound caching and servers static files. Nginx proxies requests forward to application server. Optionally Nginx protects a :term:`staging` site with a :term:`htpasswd` password, limiting potential expose to a public world.

* :term:`uWSGI` is a :term:`WSGI` server running a Python application.  It manages a pool of processes and threads running Python application code. uWSGI allows monitor, limit and terminate Python application instances guaranteeing predictable production behavior.

* :term:`Celery` runs asynchronous and background tasks. A beat process triggers scheduled tasks. There is 1-n worker processes that are responsible of executing the Python task code. See :ref:`tasks`.

* :term:`PostgreSQL` is the main SQL database where persistent data is stored and business logic requires :term:`ACID` guarantees. See :ref:`persistent` data.

* :term:`Redis` stores transient data. This includes website session and caching data (Redis database 1) and Celery task queue (Redis database 3). See :ref:`transient` data.
