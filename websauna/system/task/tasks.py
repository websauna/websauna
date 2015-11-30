"""Transaction-aware Celery task handling.

Core originally written for Warehouse project https://raw.githubusercontent.com/pypa/warehouse/master/warehouse/celery.py
"""


from celery import Task
from pyramid import scripting
from pyramid.threadlocal import get_current_request
from pyramid_tm import tm_tween_factory


class RequestAwareTask(Task):
    """Celery task which gets faux HTTPRequest instance as an argument.

    * This task only executes through ``apply_async`` if the web transaction successfully commits and only after transaction successfully commits. Thus, it is safe to pass ids to any database objects for the task and expect the task to be able to read them.

    * The first argument of the task is `request` object prepared by `pyramid.scripting.prepare`. ``request`` allows to access Pyramid registry, pass it templates as is.

    * When the task is done we call Pyramid ``closer`` to clean up the Pyramid framework bits.

    .. warn::

        ``request.route_url()`` or other URL routing functions do not work, as the proper site URL is passed from the web server to Pyramid and is not available in tasks. If you need to use proper URLs, e.g. when sending out messages, please pass those URLs to the task as an arguments for ``apply_async()`` or similar.

    Example::


    """
    abstract = True

    def __call__(self, *args, **kwargs):

        registry = self.app.conf.PYRAMID_REGISTRY

        pyramid_env = scripting.prepare(registry=registry)

        try:
            underlying = super().__call__
            request = pyramid_env["request"]
            return underlying(request, *args, **kwargs)
        finally:
            pyramid_env["closer"]()

    def apply_async(self, *args, **kwargs):
        # The API design of Celery makes this threadlocal pretty impossible to
        # avoid :(
        request = get_current_request()

        # If for whatever reason we were unable to get a request we'll just
        # skip this and call the original method to send this immediately.
        if request is None or not hasattr(request, "tm"):
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


class TransactionAwareTask(RequestAwareTask):
    """Celery task which is aware of Zope 2 transaction manager.

    * The first argument of the task is `request` object prepared by `pyramid.scripting.prepare`.

    * The task is run inside the transaction management of `pyramid_tm`. You do not need to commit the transaction at the end of the task. Failed tasks, due to exceptions, do not commit.

    Example::


    """

    abstract = True

    def __call__(self, *args, **kwargs):

        registry = self.app.conf.PYRAMID_REGISTRY

        pyramid_env = scripting.prepare(registry=registry)

        try:
            # Get bound Task.__call__
            # http://stackoverflow.com/a/1015405/315168
            underlying = Task.__call__.__get__(self, Task)

            if getattr(self, "pyramid", True):
                def handler(request):
                    underlying(request, *args, **kwargs)
            else:
                def handler(request):
                    underlying(*args, **kwargs)

            handler = tm_tween_factory(handler, pyramid_env["registry"])
            result = handler(pyramid_env["request"])
        finally:
            pyramid_env["closer"]()

        return result
