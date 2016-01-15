from pyramid.httpexceptions import HTTPFound, HTTPMovedPermanently
from slugify import slugify
from websauna.system.core.simpleroute import add_simple_route
import venusian


def redirect_view(path:str, new_path:str=None, new_route:str=None, status_code:int=302, name:str=None):
    """Generate a redirect view.

    Assign the return value of this function to a module level variable. `configuration.scan()` will pick it up and make a redirect route.

    Give a new route name or direct path where requests should be redirected.

    Example usage::

        # Product no longer available
        _cannabis_party_box = redirect_view("/can   nabis-party-box", new_route="home", status_code=301)
        _cannabis_redirect_box = redirect_view("/cannabis-extract-box", new_route="home", status_code=301)

        # SEO optimized path
        _strains = redirect_view("/strains", new_route="strains", status_code=301)

    TODO:

    * Add regex matching and such.

    ' Inefficient internal implementation

    :param path: Old path to be redirected to a new location

    :param new_route: A named route where requests are redirected.

    :param new_path: A URL path where requests are redirected.

    :param status_code: 301 for permanent redirect, 302 for temporary direct

    :param name: Optional route name. If not set it is generated from path.
    """

    assert new_route or new_path

    if not name:
        name = slugify(path) + "_redirect"

    new_path = new_path

    def redirect_view(request):

        if new_path:
            mapped_path = new_path
        else:
            mapped_path = request.route_url(new_route)

        if status_code == 302:
            return HTTPFound(mapped_path)
        elif status_code == 301:
            return HTTPMovedPermanently(mapped_path)
        else:
            raise RuntimeError("Unsupported redirect code {}", status_code)


    def callback(scanner, _name, wrapped):
        """Register a view; called on config.scan"""
        config = scanner.config

        # pylint: disable=W0142
        add_simple_route(config, path, redirect_view, append_slash=False, route_name=name)

    venusian.attach(redirect_view, callback)

    return redirect_view