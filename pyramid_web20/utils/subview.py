"""Utilities to render parts of the page exploiting Pyramid routing and traversing system."""
from pyramid.renderers import render

from zope.interface import implementer

from pyramid.interfaces import IResponse
from pyramid.view import render_view_to_iterable

@implementer(IResponse)
class SubviewResponse:
    """What subview view functions should spit out.

    Pyramid router does not try to convert this to actual HTTP response object, thus messing the routing of the main request.
    """

    def __init__(self, html):
        assert html
        self.html = html

    def __str__(self):
        return self.html

    @property
    def app_iter(self):
        return self.html


def render_subview(context, name, request, secure=True):
    # TODO: Perform component lookups by hand, don't rely on Pyramid functions
    result = render_view_to_iterable(context=context, name=name, request=request, secure=True)
    assert type(result) == str
    return result


def render_template(template, context, request):
    html = render(template, context, request=request)
    assert html
    return SubviewResponse(html)
