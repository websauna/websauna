from zope.interface import Interface


class IAdmin(Interface):
    """Marker interface for configured Admin class.     """


class IModelAdminRegistry(Interface):
    """Marker interface for configured ModelAdminManager class."""


