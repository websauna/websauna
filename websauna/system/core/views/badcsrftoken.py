"""User friend CSRF error page."""
# Standard Library
import logging

# Pyramid
from pyramid.exceptions import BadCSRFToken
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config

# Websauna
from websauna.system.http import Request


logger = logging.getLogger(__name__)


@view_config(context=BadCSRFToken, require_csrf=False)
def bad_csrf_token(context: BadCSRFToken, request: Request):
    """User friendly error page about bad CSRF token."""

    # Log this as a warning
    session = request.session
    token = session.get_csrf_token()
    logger.warn("Bad CSRF error: session: %s IP: %s cookie: %s user agent: %s", request.session.session_id, request.client_addr, token, request.user_agent)

    html = render('core/badcsrftoken.html', {}, request=request)
    resp = Response(html)
    resp.status_code = 400

    # Hint pyramid_redis_session not to generate any session cookies for this response
    resp.cache_control.public = True

    # Make sure nothing is written or no transaction left open on 500
    request.tm.abort()

    return resp
