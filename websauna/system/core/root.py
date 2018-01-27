# Pyramid
from pyramid.security import Allow
from pyramid.security import Authenticated
from pyramid.security import Everyone
from zope.interface import implementer

# Websauna
from websauna.system.core.interfaces import IRoot
from websauna.system.core.traversal import Resource


@implementer(IRoot)
class Root(Resource):
    """Pyramid routing root with default permission set up.

    These permission mappings are used unless you supply your own traversing context. For the sake of simplicity, we only declare one permission named ``authenticated`` which is given to all authenticated users.

    Permissions are as:

    * authenticated: Pseudopermission given to all authenticated users

    * superuser: equal to have SSH access to the website - can execute arbitrary Python code

    For more information see :ref:`permissions`.
    """

    __acl__ = [

        # Creaet pseudo-permission "authenticated" for all authenticated users
        (Allow, Authenticated, 'authenticated'),

        # See Notebook
        (Allow, "superuser:superuser", 'shell'),

        # All traversable resources are accesible to public by default. This permission is primarily used by sitemap to construct publicly traversable site hierarchy.
        (Allow, Everyone, 'view'),
    ]

    def __init__(self, request):
        self.request = request
        self.__name__ = ""

    @classmethod
    def root_factory(cls, request):
        """Called by Pyramid routing framework to create a new root for a request."""
        return cls(request)

    def get_title(self):
        """Title used in breadcrumbs."""
        return "Home"
