from abc import abstractmethod, ABC
import authomatic
from authomatic.core import LoginResult
from pyramid.registry import Registry
from pyramid.request import Request
from sqlalchemy.orm.attributes import flag_modified
from websauna.system.user.events import UserCreated

from websauna.utils.time import now
from websauna.system.user.interfaces import IUserModel, ISocialLoginMapper
from zope.interface import implementer


class NotSatisfiedWithData(Exception):
    """Raisen when social media login cannot proceed due to incomplete provided information.

    E.g. we need email to map the user, but the Facebook doesn't give us email because user doesn't grant the permission.
    """


@implementer(ISocialLoginMapper)
class SocialLoginMapper(ABC):
    """Map Authomatic LoginResult objects (social network logins) to our internal database users."""

    def __init__(self, registry:Registry, provider_id:str):
        """Create a mapper.

        :param registry: Pyramid configuration used to drive this mapper. Subclasses might want to query this when they create users.

        :param provider_id: String id we use to refer to this authentication source in the configuration file and in the database.
        """
        #: This is the string we use to map configuration for the
        self.provider_id = provider_id
        self.registry = registry

    @abstractmethod
    def capture_social_media_user(self, request:Request, result:LoginResult) -> IUserModel:
        """Extract social media information from the Authomatic login result in order to associate the user account."""



class EmailSocialLoginMapper(SocialLoginMapper):
    """Base class for mapping internal users to social network (OAuth) users."""


    def activate_user(request, dbsession, user):
        """Checks to perform when the user becomes a valid user for the first time.

        If this user has already started sign up process through email we need to cancel that.
        """
        user.activated_at = now()

        # Cancel any pending email activations if the user chooses the option to use social media login
        if user.activation:
            dbsession.delete(user.activation)

    def update_first_login_social_data(self, user:object, data:dict):
        """Set the initial data on the user model.

        When the user logs in from a social network for the first time (no prior logins with this email before) we fill in blanks in the user model with incoming data.

        Default action is not to set any items.

        :param data: Normalized data
        """
        pass

    def update_every_login_social_data(self, user:IUserModel, data:dict):
        """Update internal user data on every login.

        Bt default, sets user.user_data["social"]["facebook"] or user.user_data["social"]["yoursocialnetwork"] to reflect the raw data given us by ``import_social_media_user()``.
        """

        # Non-destructive update - don't remove values which might not be present in the new data
        user.user_data["social"][self.provider_id] = user.user_data["social"].get(self.provider_id) or {}
        user.user_data["social"][self.provider_id].update(data)

        # Because we are doing direct
        flag_modified(user, "user_data")

    @abstractmethod
    def import_social_media_user(self, user:authomatic.core.User) -> dict:
        """Map incoming social network data to internal data structure.

        Sometimes social networks change how the data is presented over API and you might need to do some wiggling to get it a proper shape you wish to have.

        The resulting dict must be JSON serializable as it is persisted as is.
        """

    def create_blank_user(self, user_model, dbsession, email) -> IUserModel:
        """Create a new blank user instance as we could not find matching user with the existing details."""
        user = user_model(email=email)
        dbsession.add(user)
        dbsession.flush()
        user.username = user.generate_username()
        user.registration_source = self.provider_id
        user.activated_at = now()
        return user

    def get_existing_user(self, user_model, dbsession, email):
        """Check if we have a matching user for the email already."""
        user = dbsession.query(user_model).filter_by(email=email).first()
        return user

    def get_or_create_user_by_social_medial_email(self, request:Request, user:authomatic.core.User) -> IUserModel:

        User = self.registry.queryUtility(IUserModel)

        dbsession = request.dbsession

        imported_data = self.import_social_media_user(user)
        email = imported_data["email"]

        user = self.get_existing_user(User, dbsession, email)

        if not user:
            user = self.create_blank_user(User, dbsession, email)

            request.registry.notify(UserCreated(request, user))

            self.update_first_login_social_data(user, imported_data)
            user.first_login = True

        else:
            user.first_login = False

        self.activate_user(dbsession, user)

        self.update_every_login_social_data(user, imported_data)
        return user


class FacebookMapper(EmailSocialLoginMapper):
    """Map and login Facebook OAuth users to internal users.

    You must have application created in developers.facebook.com

    The application must have its consumer_key and consumer_secret configured in the secrets config file.

    For testing: The application must have one Web site platform configured in developers.facebook.com, pointing to http://localhost:8521/ and Valid OAuth redirect URLs to http://localhost:8521/login/facebook

    """

    def import_social_media_user(self, user):
        return {
            "country": user.country,
            "timezone": user.timezone,
            "gender": user.gender,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.name,
            "link": user.link,
            "birth_date": user.birth_date,
            "city": user.city,
            "postal_code": user.postal_code,
            "email": user.email,
            "id": user.id,
            "nickname": user.nickname,
            # "address": user.address,
        }

    def update_first_login_social_data(self, user:IUserModel, data:dict):
        super(FacebookMapper, self).update_first_login_social_data(user, data)
        if not user.full_name and data.get("full_name"):
            user.full_name = data["full_name"]

    def capture_social_media_user(self, request:Request, result:LoginResult) -> IUserModel:
        """Extract social media information from the Authomatic login result in order to associate the user account."""
        assert not result.error

        # Facebook specific Authomatic call to fetch more user data from the Facebook provider
        # https://github.com/peterhudec/authomatic/issues/112
        result.user.provider.user_info_url = 'https://graph.facebook.com/me?fields=id,email,name,first_name,last_name,gender,link,timezone,verified'
        result.user.update()

        # Make user Facebook user looks somewhat legit
        assert result.user.credentials
        assert result.user.id

        if not result.user.email:
            # We cannot login if the Facebook doesnt' give us email as we use it for the user mapping
            # This can also happen when you have not configured Facebook app properly in the developers.facebook.com
            raise NotSatisfiedWithData("Email address is needed in order to user this service and we could not get one from your social media provider. Please try to sign up with your email instead.")

        user = self.get_or_create_user_by_social_medial_email(request, result.user)

        return user


class GoogleMapper(EmailSocialLoginMapper):
    """Map and login Google OAuth users to internal users.

    See :ref:`google-auth`.
    """

    def import_social_media_user(self, user):
        # http://peterhudec.github.io/authomatic/reference/providers.html#authomatic.providers.oauth2.Google
        return {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.name,
            "locale": user.locale,
            "picture": user.picture,
            "email_verified": user.email_verified,
        }

    def update_first_login_social_data(self, user:IUserModel, data:dict):
        super(GoogleMapper, self).update_first_login_social_data(user, data)
        if not user.full_name and data.get("full_name"):
            user.full_name = data["full_name"]

    def capture_social_media_user(self, request:Request, result:LoginResult) -> IUserModel:
        """Extract social media information from the Authomatic login result in order to associate the user account."""
        assert not result.error

        result.user.update()

        # Make user we got some meaningful input from the user_info_url
        assert result.user.credentials

        if not result.user.email_verified:
            raise NotSatisfiedWithData("User account email is not verified.")

        if not result.user.email:
            # We cannot login if the Facebook doesnt' give us email as we use it for the user mapping
            # This can also happen when you have not configured Facebook app properly in the developers.facebook.com
            raise NotSatisfiedWithData("Email address is needed in order to user this service and we could not get one from your social media provider. Please try to sign up with your email instead.")

        user = self.get_or_create_user_by_social_medial_email(request, result.user)

        return user


class TwitterMapper(EmailSocialLoginMapper):
    """Map Twitter OAuth users to internal users.

    See :ref:`twitter-auth`.
    """

    @staticmethod
    def _x_user_parser(user, data):
        """Monkey patched authomatic.providers.oauth1.Twitter._x_user_parser."""
        user.data = data
        # TODO: Fetch user email
        # TODO: Pending Twitter authentication request
        return user

    def import_social_media_user(self, user):
        """Pass-through Twitter auth data to user_data['social']['twitter']"""
        return user.data

    def update_first_login_social_data(self, user:IUserModel, data:dict):
        super(TwitterMapper, self).update_first_login_social_data(user, data)
        if not user.full_name and data.get("name"):
            user.full_name = data["name"]

    def capture_social_media_user(self, request:Request, result:LoginResult) -> IUserModel:
        """Extract social media information from the Authomatic login result in order to associate the user account."""
        assert not result.error

        # Monkey patch user data fetcher
        result.provider._x_user_parser = TwitterMapper._x_user_parser

        result.user.update()

        # Make user we got some meaningful input from the user_info_url
        assert result.user.credentials

        if not result.user.email:
            # We cannot login if the Facebook doesnt' give us email as we use it for the user mapping
            # This can also happen when you have not configured Facebook app properly in the developers.facebook.com
            raise NotSatisfiedWithData("Email address is needed in order to user this service and we could not get one from your social media provider. Please try to sign up with your email instead.")

        user = self.get_or_create_user_by_social_medial_email(request, result.user)

        return user
