================================
Delated tasks and scheduled jobs
================================

Websauna uses *Celery* for

* Running scheduled tasks e.g. backups

* Running delayed tasks e.g. sending email after HTTP response has been written to increase responsivity

* *pyramid_celery* package is used to provide integration between Celery and Pyramid framework. This is mostly configuration integration.

Adding a scheduled job
======================

Scheduled job is a task which is set to run on certain time interval or on a certain wall clock moment - e.g. every day 24:00.

Creating a task
---------------

Here is an example task for calling API and storing the results in Redis. In your package create file ``task.py`` and add::

    """Timed tasks."""
    import logging
    from pyramid.threadlocal import get_current_registry

    from pyramid_celery import celery_app as app
    from trees.btcaverage import RedisConverter
    from websauna.system.core.redis import get_redis

    logger = logging.getLogger(__name__)


    @app.task(name="update_conversion_rates")
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

Running the scheduler
---------------------

Celery needs to processes to run timed tasks

* *celery beat* is responsible for watching the wall clock and triggering tasks when they are about to be scheduled

* *celery worker* (multiple processes) are responsible for running the actual Python code in the tasks

Launch scripts for these are installed to your virtualenv ``bin`` folder when you install Websauna.

To launch a Celery beat do::

    celery beat -A websauna.system.celery.celery_app --ini development.ini

To launch a Celery worker do::

    celery worker -A websauna.system.celery.celery_app --ini development.ini

Supervisor configuration
^^^^^^^^^^^^^^^^^^^^^^^^

Below is a supervisor configuration Ansible template for starting the two processes. Apply and modify as necessary for your deployment.

.. code-block:: ini

    [program:celerybeat]
    command={{deploy_location}}/venv/bin/celery beat -A websauna.system.celery.celery_app --ini {{deploy_location}}/{{ site_id }}.ini --loglevel=debug
    stderr_logfile={{ deploy_location }}/logs/celery-beat.log
    directory={{ deploy_location }}
    numprocs=1
    autostart=true
    autorestart=true
    startsecs=10
    stopwaitsecs=600

    [program:celeryworker]
    command={{deploy_location}}/venv/bin/celery worker -A websauna.system.celery.celery_app --ini {{deploy_location}}/{{ site_id }}.ini --loglevel=debug
    stderr_logfile={{ deploy_location }}/logs/celery-worker.log
    directory={{ deploy_location }}
    autostart=true
    autorestart=true
    startsecs=10
    stopwaitsecs=600
    environment=C_FORCE_ROOT="true"

Delayed tasks
=============

Delayed tasks are functions which are not executed immediately, but after a certain timeout. The most common use case for these is do some processing after HTTP request - response cycle, so that the user gets the page open faster without spending time on the tasks which could be potentially handled asynchronously after HTTP response has been generated.

Below is an example which calls third party API (Twilio SMS out) - you don't want to block page render if the third party API fails or is delayed. The API is HTTP based, so calling it adds great amount of milliseconds on the request processing. The task also adds some extra delay and the SMS is not shoot up right away - it can be delayed hour or two after the user completes an order.


.. code-block:: python

    @celery_app.task
    def send_review_sms_notification(delivery_id, url):

        # Create a blank request to be passed around for templates
        request = Request.blank("/", base_url=url)
        request.registry = celery_app.conf['PYRAMID_REGISTRY']

        with transaction.manager:
            delivery = DBSession.query(models.Delivery).filter_by(id=delivery_id).first()
            customer = delivery.customer

            review_url = request.route_url("review", delivery_uuid=uuid_to_slug(delivery.uuid))
            sms.send_templated_sms(request, delivery.phone_number, "drive/sms/review.txt", locals())

    @subscriber(events.DeliveryStateChanged)
    def on_delivery_completed(event):
        """Trigger the mechanism to send SMS notification after sign off is completed."""
        request = event.request
        delivery = event.delivery

        # Trigger off review SMS
        if delivery.delivery_status == "delivered":
            reviews = models.Review.create_reviews(delivery)
            customer_id = delivery.customer.id

            # How many seconds this is
            delay = int(request.registry.settings["trees.review_sms_delay"])

            # Pass request.url as base URL so that the async task request correctly populated host name and scheme
            send_review_sms_notification.apply_async(args=(delivery.id, request.url,), countdown=delay)


Another example how to turn a call to third party API library to async::

    """Send Slack message."""
    from pyramid.settings import asbool
    from pyramid_celery import celery_app

    from slackclient import SlackClient


    def get_slack(registry):
        slack = SlackClient(registry.settings["trees.slack_token"].strip())
        return slack


    @celery_app.task
    def _call_slack_api_delayed(**kwargs):
        """Asynchronous call to Slack API.

        Do not block HTTP response head.
        """
        registry = celery_app.conf['PYRAMID_REGISTRY']
        slack = get_slack(registry)
        slack.api_call(**kwargs)


    def send_slack_message(request, channel, text):
        """API to send Slack chat notifications from at application."""

        # Slack bombing disabled by configuration
        if not asbool(request.registry.get("trees.slack", True)):
            return

        # Old, synchronous, way blocks HTTP response and decreases responsiveness
        # slack = get_slack(request.registry)
        # slack.api_call("chat.postMessage", channel=channel, text=text)

        _call_slack_api_delayed.apply_async(kwargs=dict(method="chat.postMessage", channel=channel, text=text))


Eager execution in development and unit testing
-----------------------------------------------

TODO

Inspecting task queue
=====================

Sometimes you run to issues of not being sure if the tasks are being executed or not. First check that Celery is running, both scheduler process and worker processes. Then you can check the status of Celery queue.

Start shell or do through IPython Notebook::

    ws-shell production.ini

Print out Celery queue::

    from celery.task.control import inspect
    i = inspect()
    print("Queued: {}".format(i.scheduled())
    print("Active: {}".format(i.active())


