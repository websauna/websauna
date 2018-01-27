# Pyramid
from zope.interface import Interface


class IAdmin(Interface):
    """Marker interface for configured Admin class.     """


class IModelAdmin(Interface):
    """Marker interface for scanned model admins."""
