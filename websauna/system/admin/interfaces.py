from zope.interface import Interface



class IAdmin(Interface):
    """MArker interface to store Admin instance in the Pyramid registry.

    When the application is ramped up, the admin instance is created and stored in Pyramid registry, so that other subsystems can query it to register and fetch models. This class is the utility interface declaring the admin interface object.
    """