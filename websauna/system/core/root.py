from pyramid.security import Authenticated, Allow


class Root:
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

    __name__ = ''

    _instance = None

    def __init__(self):
        pass

    @classmethod
    def get_root(cls):
        root = cls._instance
        if not root:
            root = cls._instance = Root()
        return root

    @classmethod
    def root_factory(cls, request):
        # Root is a global object, as it is referred in global traversing context objects like Admin
        return cls.get_root()


