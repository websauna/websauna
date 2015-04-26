"""The dreaded 500 page."""
from pyramid.renderers import render
from pyramid.response import Response
import transaction
import logging

from pyramid.view import view_config


logger = logging.getLogger(__name__)


@view_config(context=Exception)
def internal_server_error(context, request):

    # Here we have a hardcoded support for Sentry exception logging and pyramid_raven package
    # https://github.com/thruflo/pyramid_raven
    if hasattr(request, "raven"):
        request.raven.captureException()

    logger.exception(context)

    # The template rendering opens a new transaction which is not rolled back by Pyramid transaction machinery, because we are in a very special view. This tranaction will cause the tests to hang as the open transaction blocks Base.drop_all() in PostgreSQL. Here we have careful instructions to roll back any pending transaction by hand.
    html = render('core/internalservererror.html', {}, request=request)
    resp = Response(html)
    resp.status_code = 500
    transaction.abort()
    return resp


@view_config(route_name='error_trigger')
def error_trigger(request):
    raise RuntimeError("Test error.")