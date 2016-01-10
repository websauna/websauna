"""Events fired by websauna.system.user package."""
from websauna.system.http import Request
from websauna.system.user.models import User


class FirstLogin:
    """User logs in to the site for the first time.

    Fired upon

    * Social media login

    * After clicking email activation link
    """

    def __init__(self, request:Request, user:User):
        self.request = request
        self.user = user


class UserAuthSensitiveOperation:
    """User authentication details have changes.

    All user sessions should be dropped.

    Fired upon

    * Password change

    * Email change (TODO)
    """

    def __init__(self, request:Request, user:User, kind:str):
        """
        :param kind: What kind of operation triggered this event. Free to application to choose. E.g. "password_change", "email_change".
        :return:
        """
        self.request = request
        self.user = user
        self.kind = kind



