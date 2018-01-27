# Pyramid
from zope.interface import Interface


class IFormResources(Interface):
    """Utility to get default resources for Deform widgets."""

    def get_default_resources():
        pass
