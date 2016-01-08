from pyramid.interfaces import ISession
from pyramid.request import Request as _Request
from pyramid_redis_sessions import RedisSession
from websauna.system.admin.admin import Admin
from websauna.system.user.models import User


class Request(_Request):
    """HTTP request class.

    This is a Pyramid Request object augmented with type hinting information for Websauna-specific functionality.

    Counter-intuevily this request is also available in non-HTTP applications like command line applications and timed tasks. These applications do not get request URL from a front end HTTP webserver, but a faux request is constructed pointing to the website URL taken from ``websauna.site_url`` setting. This is to allow similar design patterns and methodology to be applied in HTTP and non-HTTP applications.
    """

    def __type_hinting__(self, user:User, session:ISession, admin:Admin):
        """A dummy helper function to tell IDEs about reify'ed variables."""
        self.user = user
        self.session = session
        self.admin = admin