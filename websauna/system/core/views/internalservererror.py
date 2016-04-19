"""The dreaded 500 page."""
from pyramid.renderers import render
from pyramid.response import Response
import transaction
import logging

from pyramid.view import view_config

logger = logging.getLogger(__name__)


@view_config(context=Exception, require_csrf=False)
def internal_server_error(context, request):
    """Generate the default internal server error page when exception falls through from a view.

    This view is marked as CSRF exempt, so that HTTP POST requests to API endpoints do not cause additional Bad CSRF exception when HTTP 500 Internal server error is raised.

    Also see https://github.com/Pylons/pyramid_tm/issues/40
    """

    # Here we have a hardcoded support for Sentry exception logging and pyramid_raven package
    # https://github.com/thruflo/pyramid_raven
    if hasattr(request, "raven"):

        user = getattr(request, "user", None)
        user_context = {}

        try:
            if user:

                # Add additional user context to the logged exception
                username = getattr(user, "friendly_name", None) or getattr(user, "username", None) or str(user)
                email = getattr(user, "email", None)
                user_context.update(dict(user=username, email=email))

            # All the session data
            session = getattr(request, "session", None)
            if session:
                session = dict(session.items())
                user_context.update(dict(session=session))
            else:
                user_context.update(dict(session="No session data available in internal_server_error()"))
        except Exception as e:
            logger.error("FAiled to Gather user and session data")
            logger.exception(e)

        request.raven.user_context(user_context)
        request.raven.captureException()

    if request.registry.settings.get("websauna.log_internal_server_error", True):
        logger.exception(context)

    # The template rendering opens a new transaction which is not rolled back by Pyramid transaction machinery, because we are in a very special view. This tranaction will cause the tests to hang as the open transaction blocks Base.drop_all() in PostgreSQL. Here we have careful instructions to roll back any pending transaction by hand.
    html = render('core/internalservererror.html', {}, request=request)
    resp = Response(html)
    resp.status_code = 500
    transaction.abort()  # https://github.com/Pylons/pyramid_tm/issues/40
    return resp


