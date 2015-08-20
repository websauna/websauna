from abc import abstractmethod, ABC
from pyramid.request import Request

from websauna.system.model import DBSession
from websauna.system.model import now
from websauna.system.user import usermixin
from websauna.system.user.interfaces import IUserClass, ISocialLoginMapper
from zope.interface import implements


class NotSatisfiedWithData(Exception):
    """Raisen when social media login cannot proceed due to incomplete provided information.

    E.g. we need email to map the user, but the Facebook doesn't give us email because user doesn't grant the permission.
    """



class SocialLoginMapper(ABC):
    """Map Authomatic user objects (social network users) to our internal database users."""

    implements(ISocialLoginMapper)

    def __init__(self, provider_id:str):
        """Create a mapper.

        :param provider_id: String id we use to refer to this authentication source in the configuration file and in the database.
        """
        #: This is the string we use to map configuration for the
        self.provider_id = provider_id

    def prepare_new_site(self, user):
        """If this is the first user on the site, initialize groups and give this user admin permissions."""
        # XXX: Move this to an event
        usermixin.check_empty_site_init(user)

    @abstractmethod
    def capture_social_media_user(self, request, result) -> IUserClass:
        """Extract social media information from the login in order to associate the user account."""



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

    def update_first_login_social_data(user:object, data:dict):
        """Set the initial data on the user model.

        When the user logs in from a social network for the first time (no prior logins with this email before) we fill in blanks in the user model with incoming data.

        Default action is not to set any items.

        :param data: Normalized data
        """
        pass

    def import_social_media_user(self, data:dict) -> dict:
        """Map incoming social network data to internal data structure.

        Sometimes social networks change how the data is presented over API and you might need to do some wiggling to get it a proper shape you wish to have.

        Default operation is no-op, data is passed through as is.
        """
        return data

    def create_blank_user(self, dbsession, email, data) -> IUserClass:
        """Create a new blank user instance as we could not find matching user with the existing details."""
        User = self.registry.queryUtility(IUserClass)
        user = User(email=email)
        dbsession.add(user)
        dbsession.flush()
        user.username = user.generate_username()
        user.registration_source = self.provider
        return user

    @abstractmethod
    def get_or_create_user_by_social_login(self, request:Request, provider:str, email:str, social_data:dict) -> IUserClass:
        """OAuth login callback views call this when when OAuth login is succesfull.

        Map the OAuth identity information to a internal user instance.

        Users are mapped by their email, so if you have multiple logins (Facebook, Twitter, by email) they all map to the same user as long as the email is not changed. However this is an implemetation detail internal to the ``SocialProvider``. Do not expect this to be guaranteed in the future as this is potential security matter and in the future each user is identified by (network id, user id) tuple.
        """
        raise NotImplementedError()

    def update_every_login_social_data(self, user:IUserClass, data:dict):
        user.social[self.provider_id] = data

    def get_existing_user(self, user_model, email, dbsession, data):
        user = dbsession.query(user_model).filter_by(email=email).first()
        return user


class FacebookMapper(EmailSocialLoginMapper):
    """Map and login Facebook OAuth users to internal users."""

    def import_social_media_user(data):
        return {
            "country": data.country,
            "timezone": data.timezone,
            "gender": data.gender,
            "first_name": data.first_name,
            "last_name": data.last_name,
            "full_name": data.first_name + " " + data.last_name,
            "link": data.link,
            "birth_date": data.birth_date,
            "city": data.city,
            "postal_code": data.postal_code,
            "email": data.email,
            "id": data.id,
            "nickname": data.nickname,
        }

    def update_first_login_social_data(self, user:IUserClass, data:dict):
        if not user.full_name and data.get("full_name"):
            user.full_name = data["full_name"]

    def get_or_create_user_by_social_login(self, request:Request, user:object) -> IUserClass:

        registry = request.registry
        User = registry.queryUtility(IUserClass)

        dbsession = DBSession

        imported_data = self.import_social_media_user(user)
        email = imported_data["email"]

        user = self.get_existing_user(dbsession, email)

        if not user:
            user = self.create_blank_user(dbsession, email)
            self.update_first_login_social_data(user, imported_data)
            user.first_login = True

            self.prepare_new_site(user)
        else:
            user.first_login = False

        self.activate_user(dbsession, user)

        self.update_every_login_social_data(user, imported_data)

        return user

    def capture_social_media_user(self, request, result) -> IUserClass:
        """Extract social media information from the login in order to associate the user account."""
        assert not result.error

        # Facebook specific Authomatic call to fetch more user data from the Facebook provider
        result.user.update()

        # Make user Facebook user looks somewhat legit
        assert result.user.credentials
        assert result.user.id

        if not result.user.email:
            # We cannot login if the Facebook doesnt' give us email as we use it for the user mapping
            raise NotSatisfiedWithData("Email address is needed in order to user this service and we could not get one from your social media provider. Please try to sign up with your email instead.")

        user = self.get_or_create_user_by_social_medial_email(request, result.user)

        return user
