===================================
Tasks - delayed and scheduled tasks
===================================

Websauna uses :term:`Celery` for

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

Use :ref:`ws-celery` command to run Celery.

To launch a Celery worker do::

    ws-celery worker -A websauna.system.task.celery.celery_app --ini development.ini

To launch a Celery beat do::

    ws-celery beat -A websauna.system.task.celery.celery_app --ini development.ini

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
    def update_btc_rate(request):
        logger.info("Fetching currency conversion rates from API to Redis")

        # Get a hold of Pyramid registry

        redis = get_redis(request.registry)
        converter = RedisConverter(redis)
        converter.update()


Another example can be found in :py:mod`websauna.system.devop.backup`.

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

Example of deferring a task executing outside HTTP request processing::

    from websauna.system.task.celery import celery_app as celery
    from websauna.system.task import TransactionalTask

    @celery.task(base=TransactionalTask)
    def send_review_sms_notification(request, delivery_id):

        # TODO: Convert global dbsession to request.dbsession
        dbsession = request.dbsession
        delivery = dbsession.query(models.Delivery).get(delivery_id)
        customer = delivery.customer

        review_url = request.route_url("review_public", delivery_uuid=uuid_to_slug(delivery.uuid))
        sms.send_templated_sms_to_user(request, customer, "drive/sms/review.txt", locals())

Then you can call this in your view::

    def my_virew(request):
        delivery = request.dbsession.query(Delivery).get(1)
        send_review_sms_notification.apply_async(args=(request, delivery.id,))


Transactional task
------------------

Transaction task happens in one database :term:`transaction`

See :py:class:`websauna.system.task.TransactionalTask`.

Non-transactional task
----------------------

If you wish to have control over transactional boundaries yourself, see :py:class:`websauna.system.task.RequestAwareTask`.

Eager execution in development and testing
------------------------------------------

When testing one might not ramp full Celery environment.

See :ref:`Celery config <celery-config>` for more details.

Configuring Celery to start with supervisor
===========================================

Below is a supervisor configuration Ansible template for starting the two processes. Apply and modify as necessary for your deployment.

.. code-block:: ini

    [program:celerybeat]
    command={{deploy_location}}/venv/bin/ws-celery beat -A websauna.system.task.celery.celery_app --ini {{deploy_location}}/{{ site_id }}.ini --loglevel=debug
    stderr_logfile={{ deploy_location }}/logs/celery-beat.log
    directory={{ deploy_location }}
    numprocs=1
    autostart=true
    autorestart=true
    startsecs=10
    stopwaitsecs=600

    [program:celeryworker]
    command={{deploy_location}}/venv/bin/ws-celery worker -A websauna.system.task.celery.celery_app --ini {{deploy_location}}/{{ site_id }}.ini --loglevel=debug
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

How many tasks queued in the default celery queue::

    from celery.task.control import inspect
    i = inspect()
    print(len(list(i.scheduled().values())[0]))

Print out Celery queue and active tasks::

    from celery.task.control import inspect
    i = inspect()
    for celery, data in i.scheduled().items():
        print("Instance {}".format(celery))
        for task in data:
            print(task)
        print("Queued: {}".format(i.scheduled()))

    print("Active: {}".format(i.active()))


Dropping task queue
-------------------

First stop worker.

Then start worker locally attacted to the terminal with --purge and it will drop all the messages::

    ws-celery worker -A websauna.system.task.celery.celery_app --ini production.ini --purge

Stop with CTRL+C.

Start worker again properly daemonized.
