import logging
import transaction

from pyramid.renderers import render
from pyramid.view import notfound_view_config
from pyramid.response import Response

logger = logging.getLogger(__name__)


@notfound_view_config()
def notfound(request):
    """Not found view which will log the 404s in the site error log."""

    request.response.status = 404

    # Try to extract some more information from request
    user = getattr(request, "user", None)
    if user:
        username = getattr(user, "friendly_name", "<unknown>")
    else:
        username = "<anomymous>"

    logger.error("404 Not Found. URL:%s user:%s ", request.url, username)

    # The template rendering opens a new transaction which is not rolled back by Pyramid transaction machinery, because we are in a very special view. This tranaction will cause the tests to hang as the open transaction blocks Base.drop_all() in PostgreSQL. Here we have careful instructions to roll back any pending transaction by hand.
    html = render('core/notfound.html', {}, request=request)
    resp = Response(html)
    transaction.abort()
    return resp
