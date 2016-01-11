from pyramid.security import Authenticated, Allow
from websauna.system.core.interfaces import IRoot
from websauna.system.core.traversal import Resource
from zope.interface import implementer


@implementer(IRoot)
class Root(Resource):
    """Pyramid routing root with default permission set up.

    These permission mappings are used unless you supply your own traversing context. For the sake of simplicity, we only declare one permission named ``authenticated`` which is given to all authenticated users.

    Permissions are as:

    * authenticated: Pseudopermission given to all authenticated users

    * superuser: equal to have SSH access to the website - can execute arbitrary Python code
    """

    __acl__ = [
        (Allow, Authenticated, 'authenticated'),
        (Allow, "superuser:superuser", 'shell'),
    ]

    def __init__(self, request):
        self.request = request
        self.__name__ = ""

    @classmethod
    def root_factory(cls, request):
        """Called by Pyramid routing framework to create a new root for a request."""
        return Root(request)

    def get_title(self):
        """Title used in breadcrumbs."""
        return "Home"


