import zope
from pyramid.interfaces import IRequest, IResponse

from zope.interface import Interface


class IUser(Interface):
    """User.

    Usually SQLAlchemy model instance of :py:class:`websauna.system.user.usermixin.UserMixin`.

    Hard requirements for User interface listed here - this is what Websauna default frontend expects from an user instance.
    """


    # How we present the user's name to the user itself.
    # Usually. Picks one of 1) full name if set 2) username if set 3) email.
    friendly_name = zope.interface.Attribute("""X blah blah""")


class IGroup(Interface):
    """User group.

    Usually SQLAlchemy model instance of :py:class:`websauna.system.user.usermixin.GroupMixin` but can be any object.
    """





class IUserModel(Interface):
    """Register utility registration which marks active User SQLAlchemy model."""


class IGroupModel(Interface):
    """Register utility registration which marks active Group SQLAlchemy model."""

class IActivationModel(Interface):
    """Register utility registration which marks active Activation SQLAlchemy model."""


class IAuthomatic(Interface):
    """Mark Authomatic instance in the registry."""


class ISocialLoginMapper(Interface):
    """Named marker interface to look up social login mappers."""


class ISiteCreator(Interface):
    """Utility that is responsible to create the initial site."""


class ILoginService(Interface):
    """Utility that is responsible to authenticate credentials, set up session and return user object.

    This is responsible to

    * Set up logged in session

    * Do post login actions
    """

    def authenticate(self, request: IRequest, user: IUser, location: str=None) -> IResponse:
        """Logs in the user.

        This is called after the user credentials have been validated.

        Sets the auth cookies and redirects to a post login page, which defaults to a view named 'index'.

        Fills in user last login time and IP data..

        :param request: Current request

        :param user: Default login service is designed to work with UserMixin compatible user classes

        :param location: Override the redirect page. If none use ``horus.login_redirect``. TODO - to be changed.
        """

    def logout(self, request: IRequest, location="/") -> IResponse:
        """Log out user from the site.

        * Terminate session

        * Show logged out message

        * Redirect the user to post login page
        """


class IOAuthLoginService(Interface):
    """Utility that is responsible to authenticate incoming OAuth logins.

    """