"""

Core originally written for Warehouse project https://raw.githubusercontent.com/pypa/warehouse/master/warehouse/celery.py
"""


from celery import Task
from pyramid import scripting
from pyramid.threadlocal import get_current_request
from pyramid_tm import tm_tween_factory


class TransactionAwareTask(Task):

    abstract = True

    def __call__(self, *args, **kwargs):
        registry = self.app.pyramid_config.registry
        pyramid_env = scripting.prepare(registry=registry)

        try:
            underlying = super().__call__
            if getattr(self, "pyramid", True):
                def handler(request):
                    return underlying(request, *args, **kwargs)
            else:
                def handler(request):
                    return underlying(*args, **kwargs)

            handler = tm_tween_factory(handler, pyramid_env["registry"])
            result = handler(pyramid_env["request"])
        finally:
            pyramid_env["closer"]()

        return result

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

