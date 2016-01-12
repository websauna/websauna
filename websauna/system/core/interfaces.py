from zope.interface import Interface


class IRoot(Interface):
    """Market interface for the root object.

    Used e.g. breadcrumbs and traversing are we in root tests.
    """
