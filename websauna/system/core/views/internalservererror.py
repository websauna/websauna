"""The dreaded 500 page."""
from pyramid.renderers import render
from pyramid.response import Response
import transaction
import logging

from pyramid.settings import asbool
from pyramid.view import view_config


from ..events import InternalServerError


logger = logging.getLogger(__name__)


@view_config(context=Exception, require_csrf=False)
def internal_server_error(context, request):
    """Generate the default internal server error page when exception falls through from a view.

    This view is marked as CSRF exempt, so that HTTP POST requests to API endpoints do not cause additional Bad CSRF exception when HTTP 500 Internal server error is raised.

    Also see https://github.com/Pylons/pyramid_tm/issues/40
    """

    request.registry.notify(InternalServerError(context, request))

    if asbool(request.registry.settings.get("websauna.log_internal_server_error", True)):
        logger.exception(context)

    request.user = None

    # The template rendering opens a new transaction which is not rolled back by Pyramid transaction machinery, because we are in a very special view. This tranasction will cause the tests to hang as the open transaction blocks Base.drop_all() in PostgreSQL. Here we have careful instructions to roll back any pending transaction by hand.
    transaction.abort()  # https://github.com/Pylons/pyramid_tm/issues/40
    html = render('core/internalservererror.html', {}, request=request)
    resp = Response(html)
    resp.status_code = 500

    # Do it again in the case rendering starts another TX
    transaction.abort()  # https://github.com/Pylons/pyramid_tm/issues/40

    return resp


