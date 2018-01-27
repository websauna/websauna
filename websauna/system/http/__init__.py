"""HTTP request and response handling."""

# Pyramid
from pyramid.interfaces import ISession
from pyramid.registry import Registry
from pyramid.request import Request as _Request
from transaction import TransactionManager

# SQLAlchemy
from sqlalchemy.orm import Session

# Websauna
from websauna.system.admin.admin import Admin
from websauna.system.core.render import OnDemandResourceRenderer
from websauna.system.user.models import User


class Request(_Request):
    """HTTP request class.

    This is a Pyramid Request object augmented with type hinting information for Websauna-specific functionality.

    To know more about request read also

    * py:class:`pyramid.request.Request` documentation

    * py:class:`webob.request.Request` documentation

    Counter-intuitiveily this request is also available in non-HTTP applications like command line applications and timed tasks. These applications do not get request URL from a front end HTTP webserver, but a faux request is constructed pointing to the website URL taken from ``websauna.site_url`` setting. This is to allow similar design patterns and methodology to be applied in HTTP and non-HTTP applications.

    By settings variables in ``__type_hinting__()`` based on arguments types allows IDEs to infer type information when you hint your views as::

        from websauna.system.http import Request

        def hello_world(request:Request):
            request.  # <-- When typing, here autocompletion kicks in.

    """

    def __type_hinting__(self, user: User, dbsession: Session, session: ISession, admin: Admin, registry: Registry, on_demand_resource_renderer: OnDemandResourceRenderer, transaction_manager: TransactionManager):
        """A dummy helper function to tell IDEs about reify'ed variables.

        :param user: The logged in user. None if the visitor is anonymous.
        :param dbsession: Current active SQLAlchemy session
        :param session: Session data for anonymous and logged in users.
        :param admin: The default admin interface of the site. Note that the site can have several admin interfaces for different purposes.
        :param registry: Pyramid registry's. E.g. :py:attr:`pyramid.registry.Registry.settings` for reading settings and :py:meth:`pyramid.registry.Registry.notify` for sending events.
        :param on_demand_resource_renderer: Manage JS and CSS files which widgets want to pull on the page dynamically
        :param transaction_manager: Transaction manager used to commit the database changes after the request completes.
        """
        self.user = user
        self.dbsession = dbsession
        self.session = session
        self.admin = admin
        self.registry = registry
        self.on_demand_resource_renderer = on_demand_resource_renderer
        self.transaction_manager = transaction_manager
        self.tm = transaction_manager
