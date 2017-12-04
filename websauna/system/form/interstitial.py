"""Display yes/no confirmation pages before taking action."""
# Standard Library
import typing as t

# Pyramid
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.session import check_csrf_token

# Websauna
from websauna.system.http import Request


class Choice:
    """Present one interstitial choice button given to a user."""

    def __init__(self, label: str, callback: t.Callable, id: str=None, css_class=None, icon_class=None):
        """
        :param label: Human readable label
        :param callback: Function called when this choice is made. Takes Must return
        :param id: Form button id. If not given derive from ``callback``.
        :param css_class: Extra CSS clases for button, like ``btn-danger``
        :param icon_class: CSS classes for ``<i>`` icon tag, like ``fa fa-remove``
        :return:
        """
        self.label = label
        self.callback = callback
        self.id = id or self.callback.__name__
        self.css_class = css_class


def process_interstitial(request: Request, choices: t.List[Choice], *args, **kwargs):
    """Check if user pressed any of the buttons on form and the choice accordingly.

    For example use case see :py:class:`websauna.system.crud.views.Delete`.

    :param args: Passed to choice callback
    :param kwargs: Passed to choice callback
    :return: HTTP response given by a choice callback
    """
    assert request.method == "POST"

    # Force CSRF check always
    check_csrf_token(request)

    for c in choices:
        if c.id in request.POST:
            return c.callback(*args, **kwargs)

    raise HTTPBadRequest("Unknown choice made")
