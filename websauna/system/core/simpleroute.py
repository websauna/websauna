"""Adaption of tomb_routes.

This code is adoption of tomb_routes https://github.com/TombProject/tomb_routes created by John Anderson.
"""

# Pyramid
from pyramid.interfaces import IViewMapperFactory
from pyramid.path import DottedNameResolver


def add_simple_route(
        config, path, target,
        append_slash=False,
        *args, **kwargs
):
    """Configuration directive that can be used to register a simple route to
    a view.

    Examples:

    with view callable::

        config.add_simple_route(
            '/path/to/view', view_callable,
            renderer='json'
        )

    with dotted path to view callable::

        config.add_simple_route(
            '/path/to/view', 'dotted.path.to.view_callable',
            renderer='json'
        )
    """

    target = DottedNameResolver().maybe_resolve(target)
    mapper = config.get_routes_mapper()

    route_name = kwargs.pop("route_name", None)
    route_name = route_name or target.__name__
    route_name_count = 0

    # Arguments passed to route
    route_kwargs = {}

    if 'accept' in kwargs:
        val = kwargs.pop('accept')
        route_kwargs['accept'] = val

    # Make it possible to custom_predicates = in the simple_route
    custom_predicates = kwargs.pop('custom_predicates', None)
    if custom_predicates:
        route_kwargs["custom_predicates"] = custom_predicates

    if 'attr' in kwargs:
        route_name += '.' + kwargs['attr']

    routes = {route.name: route for route in mapper.get_routes()}
    orig_route_name = route_name

    while route_name in routes:
        route_name = '%s_%s' % (orig_route_name, route_name_count)
        route_name_count += 1

    current_pregen = kwargs.pop('pregenerator', None)

    def pregen(request, elements, kwargs):
        if 'optional_slash' not in kwargs:
            kwargs['optional_slash'] = ''

        if current_pregen is not None:
            return current_pregen(request, elements, kwargs)
        else:
            return elements, kwargs

    orig_route_prefix = config.route_prefix
    # We are nested with a route_prefix but are trying to
    # register a default route, so clear the route prefix
    # and register the route there.
    if (path == '/' or path == '') and config.route_prefix:
        path = config.route_prefix
        config.route_prefix = ''

    if append_slash:
        path += '{optional_slash:/?}'
        config.add_route(
            route_name, path, pregenerator=pregen,
            **route_kwargs
        )
    else:
        config.add_route(
            route_name, path, pregenerator=current_pregen,
            **route_kwargs
        )

    kwargs['route_name'] = route_name

    if 'mapper' not in kwargs:
        # This should default to 'websauna.system.core.csrf.csrf_mapper_factory.<locals>.CSRFMapper'>
        mapper = config.registry.queryUtility(IViewMapperFactory)
        kwargs['mapper'] = mapper

    config.add_view(target, *args, **kwargs)
    config.commit()
    config.route_prefix = orig_route_prefix


def includeme(config):
    """Function that gets called when client code calls config.include"""
    config.add_directive('add_simple_route', add_simple_route)
