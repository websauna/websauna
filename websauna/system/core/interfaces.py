from zope.interface import Interface


class IRoot(Interface):
    """Market interface for the root object.

    Used e.g. breadcrumbs and traversing are we in root tests.
    """


class ISecrets(Interface):
    """Utility marker interface which gives us our secrets.

    Secrets is a dictionary which hold sensitive deployment data.
    """
