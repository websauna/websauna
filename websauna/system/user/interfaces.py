from horus import IUserClass
from zope.interface import Interface


class IUserClass(IUserClass):
    """Register utility registration which marks active user class."""


class IGroupClass(Interface):
    """Register utility registration which marks active Group class."""


class IAuthomatic(Interface):
    """Mark Authomatic instance in the registry."""


class ISocialLoginMapper(Interface):
    """Named marker interface to look up social login mappers."""


class ISiteCreator(Interface):
    """Utility that is responsible to create the initial site."""
