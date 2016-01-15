"""Route related helpers."""
import venusian
from websauna.system.http import Request
from websauna.utils.slug import SlugDecodeError
from websauna.utils.slug import slug_to_uuid
from .simpleroute import add_simple_route


class DecodeUUIDException(Exception):
    """Could not decode given UUID parameter."""


def decode_uuid(info: dict, request: Request, marker_string="uuid") -> bool:
    """If there is a match argument with uuid in its name convert it from Base64 encoding to UUID object.

    Example usage::

        @simple_route("/{question_uuid}", route_name="detail", custom_predicates=(decode_uuid,))
        def results(request: Request, question_uuid: UUID):
            response = "You're looking at the results of question {}."
            return Response(response.format(question_uuid))

    """
    # TODO: Make this use the view function type annotations instead of guessing type from the name.
    match = info['match']

    for key, value in match.items():
        if marker_string in key:
            try:
                match[key] = slug_to_uuid(value)
            except SlugDecodeError as e:
                import pdb ; pdb.set_trace()
                raise DecodeUUIDException("Tried to decode segment name {} value {} from base64 to UUID. Not possible.".format(key, value)) from e

    return True


class simple_route(object):
    """A set of simple defaults for Pyramid routing.

    Pyramid's URL dispatch has separate concepts for routes and views. This gives additional flexibility in that you can one route map to multiple views, using different predicates (e.g.: predicates depending on Accept header, whether request is XHR or not, etc.). In many applications, this flexibility is not needed and having both routes and views adds a bit of complexity and duplication, and reduces DRYness. This module implements some easy-to-use mechanisms that create a route and a view in one step, resulting in simpler, easier to understand code. This kind of makes Pyramid's routing look a bit more like Flask, albeit without Flask's controversial thread locals.

    Example:

    @simple_route('/path/to/view', renderer='json')
    def view_callable(request):
        return {'message': 'Hello'}
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
            if not "append_slash" in kwargs:
                append_slash = False

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
