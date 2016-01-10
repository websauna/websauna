from pyramid.interfaces import ISession
from pyramid.registry import Registry
from pyramid.request import Request as _Request
from websauna.system.admin.admin import Admin
from websauna.system.user.models import User


class Request(_Request):
    """HTTP request class.

    This is a Pyramid Request object augmented with type hinting information for Websauna-specific functionality.

    To know more about request read also

    * py:class:`pyramid.request.Request` documentation

    * py:class:`webob.request.Request` documentation

    Counter-intuevily this request is also available in non-HTTP applications like command line applications and timed tasks. These applications do not get request URL from a front end HTTP webserver, but a faux request is constructed pointing to the website URL taken from ``websauna.site_url`` setting. This is to allow similar design patterns and methodology to be applied in HTTP and non-HTTP applications.

    By settings variables in ``__type_hinting__()`` based on arguments types allows IDEs to infer type information when you hint your views as::

        from websauna.system.http import Request

        def hello_world(request:Request):
            request.  # <-- When typing, here autocompletion kicks in.

    """

    def __type_hinting__(self, user:User, session:ISession, admin:Admin, registry:Registry):
        """A dummy helper function to tell IDEs about reify'ed variables."""
        self.user = user
        self.session = session
        self.admin = admin
        self.registry = registry