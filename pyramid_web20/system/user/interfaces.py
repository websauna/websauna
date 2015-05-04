from horus import IUserClass
from zope.interface import Interface


class IUserClass(IUserClass):
    """Register utility registration which marks active user class."""


class IGroupClass(Interface):
    """Register utility registration which marks active Group class."""