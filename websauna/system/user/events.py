"""Events fired by websauna.system.user package."""
from websauna.system.http import Request
from websauna.system.user.models import User



class UserEvent:
    """User related event."""

    def __init__(self, request: Request, user: User):
        self.request = request
        self.user = user


class UserCreated(UserEvent):
    """User is created.

    Fired upon

    * Social media login

    * When sending email activation link
    """


class FirstLogin(UserEvent):
    """User logs in to the site for the first time.

    Fired upon

    * Social media login

    * After clicking email activation link

    Fired before :py:class:`Login`
    """


class Login(UserEvent):
    """User has logged in to the site.

    Fired upon

    * Social media login

    * When sending email activation link

    Fired after login data (last_login_ip) has been updated.
    """


class UserAuthSensitiveOperation(UserEvent):
    """User authentication details have changes.

    All user sessions should be dropped.

    Fired upon

    * Password change

    * Email change (TODO)
    """

    def __init__(self, request:Request, user:User, kind:str):
        """
        :param kind: What kind of operation triggered this event. Free to application to choose. E.g. "password_change", "email_change", "username_change", "enabled_change".
        :return:
        """
        self.request = request
        self.user = user
        self.kind = kind


class NewRegistrationEvent(UserEvent):
    def __init__(self, request, user, activation, values):
        super(NewRegistrationEvent, self).__init__(request, user)

        self.activation = activation
        self.values = values


class RegistrationActivatedEvent(UserEvent):
    def __init__(self, request, user, activation):
        super(RegistrationActivatedEvent, self).__init__(request, user)
        self.activation = activation


class PasswordResetEvent(UserEvent):
    def __init__(self, request, user, password):
        super(PasswordResetEvent, self).__init__(request, user)
        self.password = password