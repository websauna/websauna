"""Permission test views."""

# Pyramid
from pyramid.response import Response

# Websauna
from websauna.system.core.route import simple_route


@simple_route("test_authenticated", permission="authenticated")
def test_authenticated(request):
    return Response("<span id='ok'></span>", content_type="text/html")
