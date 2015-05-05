from pyramid.security import Authenticated, Allow


class Root:
    """Pyramid routing root with default permission set up.

    These permission mappings are used unless you supply your own traversing context. For the sake of simplicity, we only declare one permission named ``authenticated`` which is given to all authenticated users.
    """

    __acl__ = [
        (Allow, Authenticated, 'authenticated'),
    ]

    def __init__(self, request):
        self.request = request




