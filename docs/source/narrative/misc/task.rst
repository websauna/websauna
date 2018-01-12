.. _tasks:

=====
Tasks
=====

.. contents:: :local:

Introduction
============

You can achieve responsive page rendering by offloading long running blocking calls from HTTP request processing to external worker processes. Websauna uses `Celery <http://docs.celeryproject.org/en/latest/>`__ for asynchronous task processing. Celery allows asynchronous execution of delayed and scheduled tasks.

Installation
============

Make sure you have installed Websauna with ``celery`` extra dependencies to use tasks:

.. code-block:: console

    pip install websauna[celery]

See :ref:`installing_websauna` for more information. Websauna requires Celery 4.0 or newer.

Configuring Celery
==================

Websauna configures Celery using :ref:`websauna.celery_config` directive in INI settings.

Celery is configured to use :term:`Redis` as a broker between web and task processes. Unless you want to add your own scheduled tasks you do not need to change ``websauna.celery_config`` setting.

Running Celery
==============

Celery runs separate long running processes called *workers* to execute the tasks. Furthermore a separate process called *beat* needs to be run to initiate scheduled tasks. Below is an example how to run Celery on your development installation.

.. note:::

    For local development you don't need to run full Celery setup on your computer. Instead you set Celery tasks to eager execution. This means that delayed tasks are run immediately blocking the HTTP response. See **task_always_eager** Celery configuration variable. This is turned on with the default *development.ini*.

Use :ref:`ws-celery` command to run Celery. ``ws-celery`` is a wrapper around ``celery`` command supporting reading settings from :ref:`INI configuration files <config>`.

To launch a Celery worker:

.. code-block: shell

    ws-celery company/application/conf/development.ini -- worker

To launch a Celery beat do:

.. code-block: shell

    ws-celery company/application/conf/development.ini -- beat

Below is a ``run-celery.bash`` script to manage Celery for local development:

.. code-block:: bash

    #!/bin/bash
    # Launch both celery processes and kill when this script exits.
    # This script is good for running Celery for local development.
    #

    set -e
    set -u

    # http://stackoverflow.com/a/360275/315168
    trap 'pkill -f ws-celery' EXIT

    # celery command implicitly overrides root log level,
    # let's at least state it explicitly here
    ws-celery company/application/conf/development.ini -- worker --loglevel=debug &
    ws-celery company/application/conf/development.ini -- beat --loglevel=debug &

    # Wait for CTRL+C
    sleep 99999999

Managing tasks
==============

You need to register your tasks with Celery. You do this by decorating your task functions :py:func:`websauna.system.task.tasks.task` function decorator. The decorated functions and their modules must be scanned using ``self.config.scan()`` in :py:meth:`websauna.system.Initializer.configure_tasks` of your app Initializer class.

Accessing request within tasks
------------------------------

Websauna uses a custom :py:class:`websauna.system.task.celeryloader.WebsaunaLoader` Celery task loader to have ``request`` object available within your tasks. This allows you to access to ``dbsession`` and other implicit environment variables. Your tasks must have ``bind=true`` in its declaration to access the Celery task context through ``self`` argument.

Example:

.. code-block:: python

    from websauna.system.task.tasks import task
    from websauna.system.task.tasks import RetryableTransactionTask


    @task(base=RetryableTransactionTask, bind=True)
    def my_task(self: RetryableTransactionTask):
        # self.request is celery.app.task.Context
        # self.request.request is websauna.system.http.Request
        dbsession = self.get_request().dbsession
        # ...

Task dispatch on commit
-----------------------

One generally wants to have tasks runs only if HTTP request execution completes successfully. Websauna provides :py:class:`websauna.system.task.tasks.ScheduleOnCommitTask` task base class to do this.

Transaction retries
-------------------

If your task does database processing use :py:class:`websauna.system.task.RetryableTransactionTask` base class. It will mimic the behavior of ``pyramid_tm`` transaction retry machine. It tries to retry the transaction few times in the case of :ref:`transaction serialization conflict <occ>`.

Delayed tasks
-------------

Delayed tasks run tasks outside HTTP request processing. Delayed tasks take non-critical actions after HTTP response has been sent to make the server responsive. These kind of actions include calling third party APIs like sending email and SMS. Often third party APIs are slow and we don't want to delay page rendering for a site visitor.

Below is an example which calls third party API (Twilio SMS out) - you don't want to block page render if the third party API fails or is delayed. The API is HTTP based, so calling it adds great amount of milliseconds on the request processing. The task also adds some extra delay and the SMS is not shoot up right away - it can be delayed hour or two after the user completes an order.

.. note::

    All task arguments must be JSON serializable. You cannot pass any SQLAlchemy objects to Celery. Instead use primary keys of database objects.

Example of deferring a task executing outside HTTP request processing in ``tasks.py``:

.. code-block:: python

    from websauna.system.task.tasks import task
    from websauna.system.task.tasks import RetryableTransactionTask
    # ...


    @task(base=RetryableTransactionTask, bind=True)
    def send_review_sms_notification(self: RetryableTransactionTask, delivery_id: int):

        request = self.get_request()

        dbsession = request.dbsession
        delivery = dbsession.query(models.Delivery).get(delivery_id)
        customer = delivery.customer

        review_url = request.route_url("review_public", delivery_uuid=uuid_to_slug(delivery.uuid))

        # The following call to Twilio may take up to 2-5 seconds
        # We don't want to block HTTP response until Twilio is done sending SMS.
        sms.send_templated_sms_to_user(request, customer, "drive/sms/review.txt", locals())

Then you can schedule your task for delayed execution in ``views.py``:

.. code-block:: python

    def my_view(request):
        delivery = request.dbsession.query(Delivery).get(1)
        send_review_sms_notification.apply_async(args=(delivery.id,), tm=request.transaction_manager)

You also need to scan ``tasks.py`` in Initializer:

.. code-block:: python

    class MyAppInitializer(Initializer):
        """Entry point for tests stressting task functionality."""

        def configure_tasks(self):
            self.config.scan("myapp.tasks")

Scheduled tasks
---------------

Scheduled task is a job that is set to run on certain time interval or on a certain wall clock moment - e.g. every day 24:00.

Creating a task
~~~~~~~~~~~~~~~

Here is an example task for calling API and storing the results in Redis. In your package create file ``task.py`` and add:

.. code-block:: python

    from trees.btcaverage import RedisConverter

    from websauna.system.core.redis import get_redis
    from websauna.system.task import task
    from websauna.system.task import TransactionalTask


    @task(name="update_conversion_rates", base=TransactionalTask, bind=True)
    def update_btc_rate(self: TransactionalTask):
        request = self.get_request()
        redis = get_redis(request)
        converter = RedisConverter(redis)
        converter.update()


Another example can be found in :py:mod:`websauna.system.devop.backup`.

Setting schedule
~~~~~~~~~~~~~~~~

Your project INI configuration file has a section for Celery and Celery tasks. In below we register our custom task beside the default backup task

.. code-block:: ini

    [app:main]
    # ...
    websauna.celery_config =
        {
            "broker_url": "redis://localhost:6379/3",
            "accept_content": ['json'],
            "beat_schedule": {
                # config.scan() scans a Python module
                # and picks up a celery task named test_task
                "update_conversion_rates": {
                    "task": "update_conversion_rates",
                    # Run every 30 minutes
                    "schedule": timedelta(minutes=30)
                }
            }
        }

Tasks storing results
=====================

Often it is necessary that you store the result of a task. E.g.

* Long running tasks processing background batch jobs whose results get displayed in web UI

* Delayed tasks need to report if they succeeded or failed

It is best to store a result of a task in :ref:`SQLAlchemy model <models>` (complex results) or :ref:`Redis` (simple results that can be regenerated).

Here is an example task.

First we have a function that executes a long running batch job `calc_seo_assets`. It returns the result as Python dictionary that gets stored as JSON in Redis.

Example `rebuild_seo_data`:

.. code-block:: python

    from websauna.system.core.redis import get_redis

    # This is our example SQLAlchemy model for which we need to perform
    # long running tasks, one per item
    from myapp.models import Asset


    def rebuild_seo_data(request, asset: Asset):
        """Rebuild daily SEO data for an asset item. """
        key_name = "asset_seo_{}".format(asset.slug)
        logger.info("Building asset SEO %s", key_name)
        # Execute some very long running function
        data = calc_asset_seo(request, asset)

        # Store results in Redis as JSON
        redis = get_redis(request)
        redis.set(key_name, json.dumps(data))
        return data

We have several items for which we need to run this job. We iterate them in a Celery scheduled tasks that gets called twice in a day:

.. code-block:: python

    from websauna.system.task.tasks import task, WebsaunaTask
    from websauna.system.http import Request
    from websauna.system.model.retry import retryable

    # This is our example SQLAlchemy model for which we need to perform
    # long running tasks, one per item
    from myapp.models import Asset


    def _build_seo_data(request: Request):
        """Build SEO data for all assets in our database.

        We declare the function body as a separete function from the task function, so
        that this function can be called directly from ws-shell for manual testing.
        """
        dbsession = request.dbsession

        # Because doing calculations for individual jobs can be time consuming,
        # we split our jobs over several transactions, so that we do not hold
        # database locks for a single asset unnecessarily

        @retryable(tm=request.tm)
        def _get_ids():
            # Get all assets that have website set, so we know we can build SEO data for them
            asset_ids = [asset.id for asset in dbsession.query(Asset).all() if asset.other_data.get("website")]
            return asset_ids

        @retryable(tm=request.tm)
        def _run_for_id(id):
            asset = dbsession.query(Asset).get(id)
            rebuild_seo_data(request, asset)

        # Transaction 1
        ids = _get_ids()

        # Transaction 2...N
        for id in ids:
            _run_for_id(id)

    @task(name="data.build_seo_data", queue="data", bind=True, time_limit=60*30, soft_time_limit=60*15, base=WebsaunaTask)
    def build_seo_data(self: WebsaunaTask):
        """Individual asset graphs.

        This task is listed in Celery schedule in production.ini.
        """
        _build_seo_data(self.get_request())

After the task is run (by Celery or manually) the data is available in Redis and you can use it in :ref:`views` in the front end:

.. code-block:: python

    import json
    from websauna.system.core.redis import get_redis


    def fetch_seo_data(request, asset: Asset) -> dict:
        """Get SEO data build in the background task.

        :return: If data is not yet build return None, otherwise return decoded resuls.
        """
        key_name = "asset_seo_{}".format(asset.slug)

        redis = get_redis(request)
        data = redis.get(key_name)

        if data:
            return json.loads(data.decode("utf-8"))
        else:
            return None

    def my_view(request):
        seo = fetch_seo_data(self.request, self.asset)
        return seo


See also

* :ref:`occ`

* :py:func:`websauna.system.model.retry.retryable`

* :py:func:`from websauna.system.core.redis.get_redis`


More information
================

See

* :py:mod:`websauna.tests.demotasks`

* :py:mod:`websauna.system.devop.tasks`

* :py:mod:`websauna.system.task.tasks`

* :py:mod:`websauna.system.task.celeryloader`

* :py:mod:`websauna.system.task.celery`

URLs and request routes in tasks
================================

Because tasks are not served over HTTP endpoint, requests do not have URL information available in them. You need to set :ref:`websauna.site_url <websauna_site_url>` in configuration if you want to expose URLs generated within tasks.

See :py:meth:`websauna.system.http.utils.make_routable_request`.

Slack example
=============

Below is a functional example for sending messages to a Slack channel, so that you don't block HTTP response with slow Slack API.

``slack.py``:

.. code-block:: python

    """Send Slack messages.

    Asynchronous Slack caller. Must be explicitly enabled in the settings to do anything.

    In your ``settings.ini``:

        slack.enabled = true

    You need to a create a Slack app to get a token.
    https://api.slack.com/docs/oauth-test-tokens

    In your ``secrets.ini``:

        [slack]
        token = xxx

    """
    from pyramid.settings import asbool
    from slackclient import SlackClient
    from websauna.system.core.utils import get_secrets
    from websauna.system.task.tasks import ScheduleOnCommitTask
    from websauna.system.task.tasks import task


    def get_slack(registry):
        secrets = get_secrets(registry)
        slack = SlackClient(secrets["slack.token"].strip())
        return slack


    def slack_api_call(request, method, kwargs):
        """Also serve as mock patch point."""

        # Do not send anything to Slack unless explicitly enabled in settings
        if not asbool(request.registry.settings.get("slack.enabled", False)):
            return

        slack = get_slack(request.registry)
        slack.api_call(method, **kwargs)


    @task(base=ScheduleOnCommitTask, bind=True)
    def _call_slack_api_delayed(self: ScheduleOnCommitTask, method, dispatch_kwargs):
        """Asynchronous call to Slack API."""
        request = self.get_request()

        slack_api_call(request, method, dispatch_kwargs)


    def send_slack_message(request, channel, text, immediate=False, **extra_kwargs):
        """API to send Slack chat notifications from at application.

        You must have Slack API token configured in INI settings.

        Example:

        .. code-block:: python

            send_slack_message(request, "#customers", "Customer just ordering #{}".format(delivery.id))

        If you do not want deferred action and want to do a blocking Slack API call e.g. for testing:

        .. code-block:: python

            send_slack_message(request, "#customers", "Foobar", immediate=True)

        Message goes only out if the transaction is committed.
        """

        kwargs = dict(channel=channel, text=text)
        kwargs.update(extra_kwargs)

        if immediate:
            slack_api_call(request, "chat.postMessage", kwargs)
        else:
            _call_slack_api_delayed.apply_async(args=["chat.postMessage", kwargs], tm=request.tm)

Testing this with ``test_slack.py``:

.. code-block:: python

    import transaction

    from xxx.slack import send_slack_message


    def test_slack_send_message(test_request):
        """We can send messages to Slack asynchronously."""

        slack_message_queue = []

        def _test_dispatch(request, method, kwargs):
            slack_message_queue.append(dict(method=method, kwargs=kwargs))

        with mock.patch("tokenmarket.slack.slack_api_call", new=_test_dispatch):
            with transaction.manager:
                # This generates delayed task that is not send until the transaction is committed.
                send_slack_message(test_request, "#test-messages", "Foobar")

        # Celery eats exceptions happening in the tasks,
        # so we need to explicitly tests for positive outcomes of
        # any functions using Celery, regardless if Celery is in eager mode
        # or not
        msg = slack_message_queue.pop()
        assert msg["method"] == "chat.postMessage"
        assert msg["kwargs"]["channel"] == "#test-messages"
        assert msg["kwargs"]["text"] == "Foobar"


Troubleshooting
===============

Inspecting task queue
---------------------

Sometimes you run to issues of not being sure if the tasks are being executed or not. First check that Celery is running, both scheduler process and worker processes. Then you can check the status of Celery queue.

Start shell or do through IPython Notebook:

.. code-block:: console

    ws-shell ws://my/app/conf/production.ini

How many tasks queued in the default celery queue:

.. code-block:: python

    from celery.task.control import inspect
    i = inspect()
    print(len(list(i.scheduled().values())[0]))

Print out Celery queue and active tasks:

.. code-block:: python

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

Then start worker locally attacthed to the terminal with --purge and it will drop all the messages:

.. code-block:: console

    ws-celery  ws://my/app/conf/production.ini -- worker --purge

Stop with CTRL+C.

Start worker again properly daemonized.
