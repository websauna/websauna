"""Route related helpers."""
# Standard Library
import typing as t

# Pyramid
import venusian
from pyramid.config import Configurator

# Websauna
from websauna.system.http import Request

from .simpleroute import add_simple_route


class simple_route(object):
    """A set of simple defaults for Pyramid routing.

    Pyramid's URL dispatch has separate concepts for routes and views. This gives additional flexibility in that you can one route map to multiple views, using different predicates (e.g.: predicates depending on Accept header, whether request is XHR or not, etc.). In many applications, this flexibility is not needed and having both routes and views adds a bit of complexity and duplication, and reduces DRYness. This module implements some easy-to-use mechanisms that create a route and a view in one step, resulting in simpler, easier to understand code. This kind of makes Pyramid's routing look a bit more like Flask, albeit without Flask's controversial thread locals.

    .. note:: At the moment ``simple_route`` doesn't support ``viewdefaults``.

    Examples:

    .. literalinclude:: ../../../websauna/tests/viewconfig/simple_route_tests_views.py

    Respectively URLs for registered views are:

    .. literalinclude:: ../../../websauna/tests/test_simple_route.py
        :pyobject: test_registered_routes_docs
        :dedent: 11
        :lines: 4-

    """
    def __init__(self, path, *args, **kwargs):
        """Constructor just here to accept parameters for decorator"""
        self.path = path
        self.args = args
        self.kwargs = kwargs

    def __call__(self, wrapped):
        """Attach the decorator with Venusian"""
        args = self.args
        kwargs = self.kwargs

        def callback(scanner, _name, wrapped):
            """Register a view; called on config.scan"""
            config = scanner.config

            # Default to not appending slash
            if "append_slash" not in kwargs:
                kwargs['append_slash'] = False

            # pylint: disable=W0142
            add_simple_route(config, self.path, wrapped, *args, **kwargs)

        info = venusian.attach(wrapped, callback)

        if info.scope == 'class':  # pylint:disable=E1101
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if kwargs.get('attr') is None:
                kwargs['attr'] = wrapped.__name__

        return wrapped


def add_template_only_view(config: Configurator, pattern: str, name: str, template: str, view_args: t.Optional[dict]=None, route_args: t.Optional[dict]=None):
    """Adds a view which do not have a specific view function assgined.

    The view will render a template with the default template context.

    :param pattern: A path where the view is, e.g. ``/features``
    :param name: View name for ``route_url()``
    :param tempalte: A template to render
    :param view_args: kwargs passed to :py:meth:`pyramid.config.Configurator.add_view`
    :param route_args: kwargs passed to :py:meth:`pyramid.config.Configurator.add_view`
    """
    def _default_view(request):
        return {}

    config.add_route(name, pattern)
    config.add_view(view=_default_view, route_name=name, renderer=template)


def get_config_route(request: Request, config_key: str) -> str:
    """Route to a given URL from settings file."""
    settings = request.registry.settings

    try:
        return request.route_url(settings[config_key])
    except KeyError:
        return settings[config_key]
