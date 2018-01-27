"""HTTP 403 Forbidden view."""

# Pyramid
import transaction
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import forbidden_view_config


@forbidden_view_config()
def forbidden(request):
    # The template rendering opens a new transaction which is not rolled back by Pyramid transaction machinery, because we are in a very special view. This tranaction will cause the tests to hang as the open transaction blocks Base.drop_all() in PostgreSQL. Here we have careful instructions to roll back any pending transaction by hand.
    html = render('core/forbidden.html', {}, request=request)
    resp = Response(html)
    resp.status_code = 403

    # Hint pyramid_redis_session not to generate any session cookies for this response
    resp.cache_control.public = True

    transaction.abort()
    return resp
