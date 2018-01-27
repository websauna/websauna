"""The dreaded 500 page."""
# Standard Library
import logging

# Pyramid
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.settings import asbool
from pyramid.view import view_config

# Websauna
from websauna.system.core.events import InternalServerError


try:
    from pyramid_tm.reify import can_access_transaction_in_excview
    from pyramid_tm.reify import reset_transaction_aware_properties
    HAS_NEW_PYRAMID_TM = True
except ImportError:
    HAS_NEW_PYRAMID_TM = False


logger = logging.getLogger(__name__)


@view_config(context=Exception, require_csrf=False)
def internal_server_error(context, request):
    """Generate the default internal server error page when exception falls through from a view.

    This view is marked as CSRF exempt, so that HTTP POST requests to API endpoints do not cause additional Bad CSRF exception when HTTP 500 Internal server error is raised.

    Also see https://github.com/Pylons/pyramid_tm/issues/40
    """

    if HAS_NEW_PYRAMID_TM:
        if not can_access_transaction_in_excview(context, request):
            # Kill some of db aware properties in the case templates
            # might accidentally touch them
            request.__dict__["user"] = None

        else:
            # We should have db and request.user available,
            # we have just started a new transction for this view
            reset_transaction_aware_properties(request)
    else:
        request.__dict__["user"] = None

    # Tell Sentry handler to log this exception on sentry
    request.registry.notify(InternalServerError(context, request))

    if asbool(request.registry.settings.get("websauna.log_internal_server_error", True)):
        logger.exception(context)

    html = render('core/internalservererror.html', {}, request=request)
    resp = Response(html)
    resp.status_code = 500

    # Hint pyramid_redis_session not to generate any session cookies for this response
    resp.cache_control.public = True

    # Make sure nothing is written or no transaction left open on 500
    request.tm.abort()

    return resp
