"""Transaction-aware Celery task handling.

Core originally written for Warehouse project https://raw.githubusercontent.com/pypa/warehouse/master/warehouse/celery.py
"""


from celery import Task
from pyramid import scripting
from pyramid.interfaces import IRequest
from pyramid.request import Request
from pyramid.threadlocal import get_current_request
from pyramid_tm import tm_tween_factory



def _pop_request_argument(args, kwargs):

    request = None

    if args:
        args = list(args)
        request = args[0]
        args.pop(0)

    if kwargs:
        request = kwargs.pop("request", None)

    return request, args, kwargs



class BadAsyncLifeCycleException(Exception):
    pass


class RequestAwareTask(Task):
    """Celery task which gets faux HTTPRequest instance as an argument.

    * This is a helper class to be used with ``Celery.task`` function decorator.

    * The created task only executes through ``apply_async`` if the web transaction successfully commits and only after transaction successfully commits. Thus, it is safe to pass ids to any database objects for the task and expect the task to be able to read them.

    * The task run mimics the lifecycle of a Pyramid web request.

    * The decorated function first argument must be ``request``. This allows to access Pyramid registry and pass faux request object to templates as is. When task is executed asynchronously this request prepared by `pyramid.scripting.prepare` and it is not the original HTTPRequest passed when task was queued. When the task is executed synchronously using CELERY_ALWAYS_EAGER ``request`` is the original HTTPRequest object.

    .. warn::

        ``request.route_url()`` or other URL routing functions do not work, as the proper site URL is passed from the web server to Pyramid and is not available in tasks. If you need to use proper URLs, e.g. when sending out messages, please pass those URLs to the task as an arguments for ``apply_async()`` or similar.

    Example::

        '''Send Slack message.'''
        from pyramid.settings import asbool
        from slackclient import SlackClient
        from websauna.system.task import RequestAwareTask
        from websauna.system.task.celery import celery_app as celery


        def get_slack(registry):
            slack = SlackClient(registry.settings["trees.slack_token"].strip())
            return slack


        @celery.task(task=RequestAwareTask)
        def _call_slack_api_delayed(request, **kwargs):
            '''Asynchronous call to Slack API.

            '''

            registry = request.registry
            slack = get_slack(registry)

            # Slack bombing disabled by configuration
            if not asbool(request.registry.get("trees.slack", True)):
                # We could bail out early in send_slack_message, but letting it coming through here is better for test coverage
                return

            slack.api_call(**kwargs)


        def send_slack_message(request, channel, text):
            '''API to send Slack chat notifications from at application.

            You must have Slack API token configured in INI settings.

            Example::

                send_slack_message(request, "#customers", "Customer just ordering #{}".format(delivery.id)

            '''

            _call_slack_api_delayed.apply_async(kwargs=dict(request=request, method="chat.postMessage", channel=channel, text=text))


    """

    abstract = True

    def __call__(self, *args, **kwargs):
        registry = self.app.conf.PYRAMID_REGISTRY

        pyramid_env = scripting.prepare(registry=registry)

        try:
            underlying = super().__call__
            return underlying(pyramid_env["request"], *args, **kwargs)
        finally:
            pyramid_env["closer"]()

    def apply_async(self, *args, **kwargs):

        # Intercept request argumetn going to the function
        args_ = kwargs.get("args", [])
        kwargs_ = kwargs.get("kwargs", {})
        request, args_, kwargs_ = _pop_request_argument(args_, kwargs_)
        kwargs["args"] = args_
        kwargs["kwargs"] = kwargs_

        if not IRequest.providedBy(request):
            raise BadAsyncLifeCycleException("You must explicitly pass request as the first argument to asynchronous tasks as these tasks are bound to happen when the database transaction tied to the request lifecycle completes.")

        # If for whatever reason we were unable to get a request we'll just
        # skip this and call the original method to send this immediately.
        if not hasattr(request, "tm"):
            return super().apply_async(*args, **kwargs)

        # This will break things that expect to get an AsyncResult because
        # we're no longer going to be returning an async result from this when
        # called from within a request, response cycle. Ideally we shouldn't be
        # waiting for responses in a request/response cycle anyways though.
        request.tm.get().addAfterCommitHook(
            self._after_commit_hook,
            args=args,
            kws=kwargs,
        )

    def _after_commit_hook(self, success, *args, **kwargs):
        if success:
            super().apply_async(*args, **kwargs)


class TransactionalTask(RequestAwareTask):
    """Celery task which is aware of Zope 2 transaction manager.

    * The first argument of the task is `request` object prepared by `pyramid.scripting.prepare`.

    * The task is run inside the transaction management of `pyramid_tm`. You do not need to commit the transaction at the end of the task. Failed tasks, due to exceptions, do not commit.

    Example::

        from websauna.system.task.celery import celery_app as celery
        from websauna.system.task import TransactionAwareTask

        @celery.task(task=TransactionalTask)
        def send_review_sms_notification(request, delivery_id, url):

            # TODO: Convert global dbsession to request.dbsession
            delivery = DBSession.query(models.Delivery).filter_by(id=delivery_id).first()
            customer = delivery.customer

            review_url = request.route_url("review_public", delivery_uuid=uuid_to_slug(delivery.uuid))
            sms.send_templated_sms_to_user(request, customer, "drive/sms/review.txt", locals())


        @subscriber(events.DeliveryStateChanged)
        def on_delivery_completed(event):
            '''Trigger the mechanism to send SMS notification after sign off is completed.'''
            request = event.request
            delivery = event.delivery
            assert delivery.id

            # Trigger off review SMS
            if delivery.delivery_status == "delivered":

                reviews = models.Review.create_reviews(delivery)
                customer_id = delivery.customer.id
                delay = int(request.registry.settings["trees.review_sms_delay"])

                # Pass request.url as base URL so that the async task request correctly populated host name and scheme
                send_review_sms_notification.apply_async(args=(request, delivery.id, request.host_url,), countdown=delay)


    """

    abstract = True

    def __call__(self, *args, **kwargs):

        registry = self.app.conf.PYRAMID_REGISTRY

        pyramid_env = scripting.prepare(registry=registry)

        try:
            # Get bound Task.__call__
            # http://stackoverflow.com/a/1015405/315168
            underlying = Task.__call__.__get__(self, Task)

            def handler(request):
                underlying(request, *args, **kwargs)

            handler = tm_tween_factory(handler, pyramid_env["registry"])
            result = handler(pyramid_env["request"])
        finally:
            pyramid_env["closer"]()

        return result
