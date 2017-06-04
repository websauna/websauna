"""Patched Google provider until we get upstream fixed.

https://github.com/peterhudec/authomatic/issues/153
"""

from authomatic import core
from authomatic.providers.oauth2 import OAuth2


class Google(OAuth2):
    """
    Google |oauth2| provider.

    * Dashboard: https://console.developers.google.com/project
    * Docs: https://developers.google.com/accounts/docs/OAuth2
    * API reference: https://developers.google.com/gdata/docs/directory
    * API explorer: https://developers.google.com/oauthplayground/

    Supported :class:`.User` properties:

    * email
    * first_name
    * gender
    * id
    * last_name
    * link
    * locale
    * name
    * picture

    Unsupported :class:`.User` properties:

    * birth_date
    * city
    * country
    * nickname
    * phone
    * postal_code
    * timezone
    * username

    .. |oauth2| replace:: oauth2
    .. note::

        To get the user info, you need to activate the **Google+ API**
        in the **APIs & auth >> APIs** section of the`Google Developers Console
        <https://console.developers.google.com/project>`__.

    """

    user_authorization_url = 'https://accounts.google.com/o/oauth2/auth'
    access_token_url = 'https://accounts.google.com/o/oauth2/token'
    user_info_url = 'https://www.googleapis.com/oauth2/v3/userinfo?alt=json'

    user_info_scope = ['profile',
                       'email']

    supported_user_attributes = core.SupportedUserAttributes(
        id=False,
        email=True,
        name=True,
        first_name=True,
        last_name=True,
        locale=True,
        picture=True,

        # No longer supported as of 2016-08
        link=False,
        gender=False,
    )

    def __init__(self, *args, **kwargs):
        super(Google, self).__init__(*args, **kwargs)

        # Handle special Google requirements to be able to refresh the access token.
        if self.offline:
            if 'access_type' not in self.user_authorization_params:
                # Google needs access_type=offline param in the user authorization request.
                self.user_authorization_params['access_type'] = 'offline'
            if 'approval_prompt' not in self.user_authorization_params:
                # And also approval_prompt=force.
                self.user_authorization_params['approval_prompt'] = 'force'

    @classmethod
    def _x_request_elements_filter(cls, request_type, request_elements,
                                   credentials):
        """
        Google doesn't accept client ID and secret to be at the same time in
        request parameters and in the basic authorization header in the
        access token request.
        """
        if request_type is cls.ACCESS_TOKEN_REQUEST_TYPE:
            params = request_elements[2]
            del params['client_id']
            del params['client_secret']
        return request_elements

    @staticmethod
    def _x_user_parser(user, data):

        user.email = data.get('email')
        user.name = data.get('name')
        user.first_name = data.get('given_name', '')
        user.last_name = data.get('family_name', '')
        user.locale = data.get('locale', '')
        user.picture = data.get('picture', '')

        # Special attribute if email has been verified
        user.email_verified = data.get("email_verified")
        user.hosted_domain = data.get("hd")
        return user

    def _x_scope_parser(self, scope):
        """
        Google has space-separated scopes
        """
        return ' '.join(scope)


# Needed for Authomatic magic
PROVIDER_ID_MAP = [Google]
