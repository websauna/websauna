===================================
Tasks - delayed and scheduled tasks
===================================

Websauna uses *Celery* for

* Running scheduled tasks e.g. backups

* Running delayed tasks e.g. sending email after HTTP response has been written to increase responsivity

* *pyramid_celery* package is used to provide integration between Celery and Pyramid framework. This is mostly configuration integration.


Celery basics
=============

Celery is a Python framework for running asynchronous and scheduled tasks in separate processes.

* Tasks do not run in the same process or Python virtual machine as the web requests are handled

* In fact, tasks can run on a different computer altogether

* Celery worker process executes task functions

* Celery beat process triggers execution of scheduled tasks

* Websauna is configured to use Celery through Redis. The default broken locations are localhost Redis database 3 for deployment, localhost Redis database 15 for testing.

* All function arguments going into tasks must be JSON serializable. You cannot pass complex Python objects, like HTTPRequest, directly to the tasks. This is because tasks live in separate process and Python virtual machine.

Task types
==========

Websauna offers to Celery task classes

* :py:class:`websauna.system.task.TransactionalTask`: Everything in the task is completed in one database transaction which commits when the transaction finishes. If an exception is raised no database changes are made.

* :py:class:`websauna.system.task.RequestAwareTask`: There is no transaction lifecycle and the task author is responsible for committed any changes. Good for tasks which do not read or write database.

* If called through ``delay`` or ``apply_async`` the tasks go to Celery queue only if the current :py:class:`pyramid.request.Request` successfully finishes and the transaction is committed.

* Both task classes supply :py:class:`pyramid.request.Request` dummy request as the first argument for the task functions. This allows you to access Pyramid registry (``request.registry``) or pass the dummy request to template functions. Please note that this is a dummy request object not coming from a web server and thus cannot be used for generating URLs.

Running Celery
==============

Celery needs to run to process the tasks. Below is an example how to run Celery on your development installation.

Launch scripts for these are installed to your virtualenv ``bin`` folder when you install Websauna.

To launch a Celery worker do::

    celery worker -A websauna.system.task.celery.celery_app --ini development.ini

To launch a Celery beat do::

    celery beat -A websauna.system.task.celery.celery_app --ini development.ini

Scheduled tasks
===============

Scheduled job is a task which is set to run on certain time interval or on a certain wall clock moment - e.g. every day 24:00.

Creating a task
---------------

Here is an example task for calling API and storing the results in Redis. In your package create file ``task.py`` and add::

    """Timed tasks."""
    import logging
    from pyramid.threadlocal import get_current_registry

    from trees.btcaverage import RedisConverter
    from websauna.system.core.redis import get_redis
    from websauna.system.task.celery import celery_app as celery
    from websauna.system.task.TransactionalTask import TransactionalTask

    logger = logging.getLogger(__name__)


    @celery.task(name="update_conversion_rates", base=TransactionalTask)
    def update_btc_rate():
        logger.info("Fetching currency conversion rates from API to Redis")

        # Get a hold of Pyramid registry
        registry = get_current_registry()

        redis = get_redis(registry)
        converter = RedisConverter(redis)
        converter.update()

Scheduling task
---------------

Your project INI configuration file has a section for Celery and Celery tasks. In below we register our custom task beside the default backup task::

    [celery]
    CELERY_IMPORTS =
        websauna.system.devop.tasks
        trees.tasks

    [celerybeat:backup]
    task = backup
    type = timedelta
    schedule = {"hours": 24}

    [celerybeat:update_conversion_rates]
    task = update_conversion_rates
    type = timedelta
    schedule = {"hours": 1}

Delayed tasks
=============

Delayed tasks are functions which are not executed immediately, but after a certain timeout. The most common use case for these is do some processing after HTTP request - response cycle, so that the user gets the page open faster without spending time on the tasks which could be potentially handled asynchronously after HTTP response has been generated.

Below is an example which calls third party API (Twilio SMS out) - you don't want to block page render if the third party API fails or is delayed. The API is HTTP based, so calling it adds great amount of milliseconds on the request processing. The task also adds some extra delay and the SMS is not shoot up right away - it can be delayed hour or two after the user completes an order.

Transactional task
------------------

See :py:class:`websauna.system.task.TransactionalTask`.

Non-transactional task
----------------------

See :py:class:`websauna.system.task.RequestAwareTask`.

Eager execution in development and testing
------------------------------------------

When testing one might not ramp full Celery environment.


Configuring Celery to start with supervisor
===========================================

Below is a supervisor configuration Ansible template for starting the two processes. Apply and modify as necessary for your deployment.

.. code-block:: ini

    [program:celerybeat]
    command={{deploy_location}}/venv/bin/celery beat -A websauna.system.task.celery.celery_app --ini {{deploy_location}}/{{ site_id }}.ini --loglevel=debug
    stderr_logfile={{ deploy_location }}/logs/celery-beat.log
    directory={{ deploy_location }}
    numprocs=1
    autostart=true
    autorestart=true
    startsecs=10
    stopwaitsecs=600

    [program:celeryworker]
    command={{deploy_location}}/venv/bin/celery worker -A websauna.system.task.celery.celery_app --ini {{deploy_location}}/{{ site_id }}.ini --loglevel=debug
    stderr_logfile={{ deploy_location }}/logs/celery-worker.log
    directory={{ deploy_location }}
    autostart=true
    autorestart=true
    startsecs=10
    stopwaitsecs=600
    environment=C_FORCE_ROOT="true"


Troubleshooting
===============

Inspecting task queue
---------------------

Sometimes you run to issues of not being sure if the tasks are being executed or not. First check that Celery is running, both scheduler process and worker processes. Then you can check the status of Celery queue.

Start shell or do through IPython Notebook::

    ws-shell production.ini

Print out Celery queue::

    from celery.task.control import inspect
    i = inspect()
    print("Queued: {}".format(i.scheduled())
    print("Active: {}".format(i.active())