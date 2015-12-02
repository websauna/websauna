from zope.interface import Interface


class IAdmin(Interface):
    """Marker interface for configured Admin class.     """


class IModel(Interface):
    """Marker interface for known model class definitions."""


class IModelAdmin(Interface):
    """Marker interface for scanned model admins."""


