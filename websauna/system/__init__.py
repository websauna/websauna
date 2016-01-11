"""Websauna framework initialization."""
import logging
import os

from pyramid.config import Configurator
from pyramid.interfaces import IDebugLogger
from pyramid.path import DottedNameResolver
from pyramid.settings import aslist
from pyramid.settings import asbool

from pyramid_mailer.interfaces import IMailer
from pyramid_deform import configure_zpt_renderer
from websauna.system.admin.modeladmin import configure_model_admin
from websauna.system.model.utils import attach_model_to_base
from websauna.utils.configincluder import IncludeAwareConfigParser


class SanityCheckFailed(Exception):
    """Looks like the application has configuration which would fail to run."""


class Initializer:
    """Initializer is responsible to ramp up the frameworks and subsystems.

    There exist one ``Initializer`` instance which you create in your WSGI application constructor.

    * You subclass the default ``Initializer`` provider by Websauna

    * You override the methods for the parts where you want to customize the default Websauna behavior

    * You also need to include addons and other Pyramid package configurations. This is usually done by calling ``self.config.include("your_pyramid_package")``.

    * You can add your own application specific view initializations, like ``self.config.scan()`` for your application Python modules to register ``@view_config`` directives in those.

    See :py:meth:`websauna.system.Initializer.run` for linear initialization order.
    """

    def __init__(self, global_config:dict, settings:dict=None, configurator:Configurator=None):
        """

        :param global_config: Dictionary as passed to WSGI entry point.

        :param settings: DEPRECATED. Extra settings as passed to WSGI entry point. TODO: How to handle these?

        :param config: Configurator passed by another Pyramid app entry point. If given use this. If not given extra the config file from ``global_config`` and then create a ``Configurator`` for it. This is usually given when Initializer is used with addon.
        """
        if not settings:
            settings = IncludeAwareConfigParser.retrofit_settings(global_config)

        #: This is the refer    ence to the config file which started our process. We need to later pass it to Notebook.
        settings["websauna.global_config"] = global_config
        self.global_config = global_config

        self.config = self.create_configurator(settings)

        #: Python module which provides Horus models
        self.user_models_module = None

        #: Reference to Celery app instance
        self.celery = None

        self.settings = settings

        #: Flag to tell if we need to do sanity check for redis sessiosn
        self._has_redis_sessions = False

    def create_configurator(self, settings):
        """Create Pyramid Configurator instance."""
        configurator = Configurator(settings=settings)
        return configurator

    def get_cache_max_age(self, settings):
        """Get websauna.cache_max_age setting and convert it to seconds.

        :return: None for no caching or cache_max_age as seconds
        """

        cache_max_age = settings.get("websauna.cache_max_age")
        if (not cache_max_age) or (not cache_max_age.strip()):
            return None
        else:
            return int(cache_max_age)

    def add_cache_buster(self, asset_spec:str):
        """Adds configured cache busting capability to a given static assets.

        You need to call this for every added ``config.add_static_view()``.

        Override this to customize cache busting mechanism on your site. The default implementation uses ``PathSegmentMd5CacheBuster``.
        """

        try:
            # Pyramid 1.6b3+
            from pyramid.static import PathSegmentMd5CacheBuster
            BusterClass = PathSegmentMd5CacheBuster
        except ImportError:
            # Pyramid 1.6b3
            from pyramid.static import QueryStringCacheBuster
            BusterClass = QueryStringCacheBuster

        cachebust = asbool(self.settings.get("websauna.cachebust"))
        if cachebust:
            self.config.add_cache_buster(asset_spec, BusterClass())

    def configure_logging(self, settings):
        """Create and set Pyramid debug logger.

        Please note that most o the logging is configured through the configuration file and that should be the primary way to do it.
        """

        # Extract logging configuration from INI
        from websauna.utils.configincluder import setup_logging

        setup_logging(self.global_config["__file__"])

        # Make sure we can target Pyramid router debug messages in logging configuration
        pyramid_debug_logger = logging.getLogger("pyramid_debug")
        self.config.registry.registerUtility(pyramid_debug_logger, IDebugLogger)

    def configure_horus(self, settings):
        """Configure user and group SQLAlchemy models, login and sign up views."""

        # Avoid importing horus if not needed as it will bring in its own SQLAlchemy models and dirties our SQLAlchemy initialization

        # TODO: This will be removed

        from hem.interfaces import IDBSession
        from horus.interfaces import IRegisterSchema
        from horus.interfaces import ILoginSchema
        from horus import IResetPasswordSchema
        from websauna.system.user.interfaces import IUserClass, IGroupClass
        from websauna.system.user import schemas
        from websauna.system.user import horus as horus_init

        # Tell horus which SQLAlchemy scoped session to use:
        registry = self.config.registry
        registry.registerUtility(None, IDBSession)

        # self.config.include("horus")
        horus_init.includeme(self.config)

        # self.config.scan_horus(users_models)
        self.config.registry.registerUtility(schemas.RegisterSchema, IRegisterSchema)
        self.config.registry.registerUtility(schemas.LoginSchema, ILoginSchema)
        self.config.registry.registerUtility(schemas.ResetPasswordSchema, IResetPasswordSchema)

    def configure_mailer(self, settings):
        """Configure outgoing email backend based on the INI settings."""

        settings = settings.copy()

        # Empty values are not handled gracefully, so mutate them here before passing forward to mailer
        if settings.get("mail.username", "x") == "":
            settings["mail.username"] = None

        if settings.get("mail.password", "x") == "":
            settings["mail.password"] = None

        mailer_class = settings.get("websauna.mailer", "")
        if mailer_class in ("mail", ""):
            # TODO: Make mailer_class explicit so we can dynamically load pyramid_mail.Mailer
            # Default
            from pyramid_mailer import mailer_factory_from_settings
            mailer = mailer_factory_from_settings(settings)
            self.config.registry.registerUtility(mailer, IMailer)
        else:
            # debug backend
            resolver = DottedNameResolver()
            mailer_cls = resolver.resolve(mailer_class)
            mailer = mailer_cls()

            self.config.registry.registerUtility(mailer, IMailer)

    def configure_templates(self):
        from websauna.system.core import templatecontext

        # Jinja 2 templates as .html files
        self.config.include('pyramid_jinja2')
        self.config.add_jinja2_renderer('.html')
        self.config.add_jinja2_renderer('.txt')
        self.config.add_jinja2_renderer('.css')
        self.config.add_jinja2_renderer('.xml')

        # Some Horus templates need still Mako in place - TODO: remove this when all templates are converted
        self.config.include('pyramid_mako')

        self.config.include("websauna.system.core.templatecontext")

        # Make Deform widgets aware of our widget template paths
        configure_zpt_renderer(["websauna.system:form/templates/deform"])

        # Add core templates to the search path
        self.config.add_jinja2_search_path('websauna.system:core/templates', name='.html')
        self.config.add_jinja2_search_path('websauna.system:core/templates', name='.txt')
        self.config.add_jinja2_search_path('websauna.system:core/templates', name='.xml')

    def configure_authentication(self, settings, secrets):
        """Set up authentication and authorization policies.

        For more information see Pyramid auth documentation.
        """
        import pyramid.tweens
        from websauna.system.auth.policy import SessionAuthenticationPolicy
        from websauna.system.auth.principals import resolve_principals
        from websauna.system.auth.authentication import get_request_user
        from pyramid.authorization import ACLAuthorizationPolicy

        authn_policy = SessionAuthenticationPolicy(callback=resolve_principals)
        authz_policy = ACLAuthorizationPolicy()
        self.config.set_authentication_policy(authn_policy)
        self.config.set_authorization_policy(authz_policy)

        self.config.add_request_method(get_request_user, 'user', reify=True)

        self.config.add_tween("websauna.system.auth.tweens.SessionInvalidationTweenFactory", over=pyramid.tweens.MAIN)

        # Grab incoming auth details changed events
        from websauna.system.auth import subscribers
        self.config.scan(subscribers)

    def configure_panels(self, settings):
        self.config.include('pyramid_layout')

    def configure_authomatic(self, settings, secrets):
        """Configure Authomatic social logins.

        Read enabled logins from the configuration file.

        Read consumer secrets from a secrets.ini.
        """
        # Add OAuth 2 generic endpoint

        import authomatic
        from websauna.system.user.interfaces import IAuthomatic, ISocialLoginMapper

        self.config.add_route('login_social', '/login/{provider_name}')

        social_logins = aslist(settings.get("websauna.social_logins", ""))

        if not social_logins:
            return

        authomatic_config = {}

        authomatic_secret = secrets["authomatic.secret"]

        resolver = DottedNameResolver()

        # Quick helper to access settings
        def xget(section, key):
            value = secrets.get(section + "." + key)
            assert value is not None, "Missing secret settings for [{}]: {}".format(section, key)
            return value

        for login in social_logins:

            authomatic_config[login] = {}
            authomatic_config[login]["consumer_key"] = xget(login, "consumer_key")
            authomatic_config[login]["consumer_secret"] = xget(login, "consumer_secret")
            authomatic_config[login]["scope"] = aslist(xget(login, "scope"))

            # TODO: Class is not a real secret, think smarter way to do this
            authomatic_config[login]["class_"] = resolver.resolve(xget(login, "class"))

            # Construct social login mapper
            mapper_class = xget(login, "mapper")
            if mapper_class:
                mapper_class = resolver.resolve(mapper_class)
                mapper = mapper_class(self.config.registry, login)
                self.config.registry.registerUtility(mapper, ISocialLoginMapper, name=login)

        # Store instance
        instance = authomatic.Authomatic(config=authomatic_config, secret=authomatic_secret)
        self.config.registry.registerUtility(instance, IAuthomatic)

    def configure_database(self, settings):
        """Configure database.

        Calls py:func:`websauna.system.model.meta.includeme`.
        """
        self.config.include(".model.meta")

    def configure_instrumented_models(self):
        """Configure models from third party addons and dynamic SQLAlchemy fields which need access to the configuration.

        Third party addons might need references to configurable models which are not available at the import time. One of these models is user - you can supply your own user model. However third party addon models might want to build foreign key relationships to this model. Thus, ``configure_instrumented_models()`` is an initialization step which is called when database setup is half way there and you want to throw in some extra models in.

        This exposes ``Configurator`` to SQLAlchemy through ``websauna.system.model.meta.Base.metadata.pyramid_config`` variable.
        """

        # Expose Pyramid configuration to classes
        from websauna.system.model.meta import Base
        Base.metadata.pyramid_config = self.config

    def configure_error_views(self):

        settings = self.settings

        # Forbidden view overrides helpful auth debug error messages,
        # so pull in only when really needed

        if not asbool(settings["pyramid.debug_authorization"]):
            from websauna.system.core.views import forbidden
            self.config.scan(forbidden)

        if not asbool(settings["pyramid.debug_notfound"]):
            from websauna.system.core.views import notfound
            self.config.scan(notfound)

        # Internal server error must be only activated in the production mode, as it clashes with pyramid_debugtoolbar
        if "pyramid_debugtoolbar" not in aslist(settings["pyramid.includes"]):
            from websauna.system.core.views import internalservererror
            self.config.scan(internalservererror)

        if settings.get("websauna.error_test_trigger", False):
            from websauna.system.core.views import errortrigger
            self.config.scan(errortrigger)
            self.config.add_route('error_trigger', '/error-trigger')

    def configure_root(self):
        """Root object defines permissions for route URLs which have not their own traversing context.

        http://pyramid-tutorials.readthedocs.org/en/latest/getting_started/10-security/
        """
        from websauna.system.core.root import Root
        self.config.set_root_factory(Root.root_factory)

    def configure_views(self):
        from websauna.system.core.views import home
        self.config.add_route('home', '/')
        self.config.scan(home)

    def configure_sitemap(self, settings):
        """Configure sitemap generation for your site.

        By default this is not configured and nothing is done.
        """

    def configure_static(self):
        """Configure static asset serving and cache busting.

        By default we serve only core Websauna assets. Override this to add more static asset declarations to your app.

        http://docs.pylonsproject.org/projects/pyramid/en/1.6-branch/narr/assets.html#static-assets-section
        """
        self.config.add_static_view('websauna-static', 'websauna.system:static')
        self.add_cache_buster("websauna.system:static/")

    def configure_sessions(self, settings, secrets):
        """Configure session storage."""

        from websauna.system.core.session import set_creation_time_aware_session_factory

        session_secret = secrets["session.secret"]

        # TODO: Make more boilerplate here so that we pass secret in more sane way
        self.config.registry.settings["redis.sessions.secret"] = session_secret
        self.config.include("pyramid_redis_sessions")

        # Set a flag to perform Redis session check later and prevent web server start if Redis is down
        self._has_redis_sessions = True

        set_creation_time_aware_session_factory(self.config)

    def configure_admin(self, settings):
        """Configure admin ux.

        Register templates and views for admin interface.
        """

        from websauna.system.admin import views
        from websauna.system.admin import subscribers
        from websauna.system.admin.admin import Admin
        from websauna.system.admin.interfaces import IAdmin
        from websauna.system.admin.interfaces import IAdmin
        from websauna.system.admin.utils import get_admin

        # Register default Admin provider
        config = self.config
        config.registry.registerUtility(Admin, IAdmin)

        # Set up model lookup
        configure_model_admin(config)

        config.add_jinja2_search_path('websauna.system.admin:templates', name='.html')
        config.add_jinja2_search_path('websauna.system.admin:templates', name='.txt')

        config.add_route('admin_home', '/admin/', factory="websauna.system.admin.utils.get_admin")
        config.add_route('admin', "/admin/*traverse", factory="websauna.system.admin.utils.get_admin")

        config.add_panel('websauna.system.admin.views.default_model_admin_panel')
        config.scan(views)
        config.scan(subscribers)

        self.config.add_request_method(get_admin, 'admin', reify=True)

    def configure_forms(self, settings):

        # Add custom SQLAlchemy <-> Deform type mapping
        # Importing is enough to trigger SQLAlchemy override
        from websauna.system.form import types

    def configure_crud(self, settings):
        """CRUD templates and views."""

        # Add our template to search path
        self.config.add_jinja2_search_path('websauna.system.crud:templates', name='.html')
        self.config.add_jinja2_search_path('websauna.system.crud:templates', name='.txt')

        from websauna.system.crud import views
        self.config.scan(views)

    def configure_user_models(self, settings):
        """Plug in user models.

        Connect chosen user model to SQLAlchemy model Base. Also set up :py:class:`websauna.system.user.usermixin.SiteCreator` logic - what happens when the first user logs in.
        """
        from websauna.system.user import models
        from websauna.system.model.meta import Base
        from websauna.system.user.interfaces import IGroupClass, IUserClass, ISiteCreator
        from websauna.system.user.usermixin import SiteCreator
        from horus.interfaces import IActivationClass

        attach_model_to_base(models.User, Base)
        attach_model_to_base(models.Group, Base)
        attach_model_to_base(models.Activation, Base)
        attach_model_to_base(models.UserGroup, Base)

        # Mark active user and group class
        registry = self.config.registry
        registry.registerUtility(models.User, IUserClass)
        registry.registerUtility(models.Group, IGroupClass)

        site_creator = SiteCreator()
        registry.registerUtility(site_creator, ISiteCreator)

        # TODO: Get rid of Horus
        registry.registerUtility(models.Activation, IActivationClass)

    def configure_user(self, settings, secrets):
        """Configure user model, sign in and sign up subsystem."""
        from websauna.system.user import views
        from horus.resources import UserFactory

        # Configure user models base package
        # TODO: Get rid of Horus
        self.configure_horus(settings)

        self.configure_user_models(settings)

        # Configure authentication and
        self.configure_authentication(settings, secrets)

        # Configure social logins
        self.configure_authomatic(settings, secrets)

        self.config.add_jinja2_search_path('websauna.system:user/templates', name='.html')
        self.config.add_jinja2_search_path('websauna.system:user/templates', name='.txt')

        self.config.scan(views)
        self.config.add_route('waiting_for_activation', '/waiting-for-activation')
        self.config.add_route('registration_complete', '/registration-complete')
        self.config.add_route('login', '/login')
        self.config.add_route('logout', '/logout')
        self.config.add_route('forgot_password', '/forgot-password')
        self.config.add_route('reset_password', '/reset-password/{code}')
        self.config.add_route('register', '/register')
        self.config.add_route('activate', '/activate/{user_id}/{code}', factory=UserFactory)

    def configure_user_admin(self, settings):
        import websauna.system.user.admins
        import websauna.system.user.adminviews
        self.config.scan(websauna.system.user.admins)
        self.config.scan(websauna.system.user.adminviews)

    def configure_notebook(self, settings):
        """Setup pyramid_notebook integration."""
        import websauna.system.notebook.views
        self.config.add_route('admin_shell', '/notebook/admin-shell')
        self.config.add_route('shutdown_notebook', '/notebook/shutdown')
        self.config.add_route('notebook_proxy', '/notebook/*remainder')
        self.config.scan(websauna.system.notebook.views)

    def configure_tasks(self, settings):
        """Scan all Python modules with asynchoronou sna dperiodic tasks to be imported."""

        # Importing the task is enough to add it to Celerybeat working list
        from websauna.system.devop import tasks  # noqa

    def configure_scheduler(self, settings):
        """Configure Celery."""

        # Patch pyramid_celery to use our config loader
        import websauna.system.task.celery

        # Patch various paster internals
        from websauna.utils.configincluder import monkey_patch_paster_config_parser
        monkey_patch_paster_config_parser()
        self.config.include("pyramid_celery")

        self.config.configure_celery(self.global_config["__file__"])

        self.celery = websauna.system.task.celery.celery_app

    def read_secrets(self, settings):
        """Read secrets configuration file.

        Stores API keys, such.
        """
        # Secret configuration diretives
        from websauna.system.core import secrets

        secrets_file = settings.get("websauna.secrets_file")
        if not secrets_file:
            return {}

        _secrets = secrets.read_ini_secrets(secrets_file)
        self.config.registry.registerUtility(_secrets, secrets.ISecrets)
        return _secrets

    def configure_addons(self):
        """Override this method to include Websauna addons for your app.

        Websauna addons are created with ``websauna_addon`` scaffold.

        By default do nothing.
        """

    def run(self):
        """Run the initialization and prepare Pyramid subsystems.

        This is the main entry for ramping up a Websauna application.
        We go through various subsystem inits.
        """

        # TODO: Remove passing settings to methods as an argument
        settings = self.settings

        _secrets = self.read_secrets(settings)

        self.configure_logging(settings)

        # Serving
        self.configure_templates()
        self.configure_static()

        # Forms
        self.configure_forms(settings)
        self.configure_crud(settings)

        # Email
        self.configure_mailer(settings)

        # Timed tasks
        self.configure_scheduler(settings)
        self.configure_tasks(settings)

        # Core view and layout related
        self.configure_root()
        self.configure_error_views()
        self.configure_views()
        self.configure_panels(settings)
        self.configure_sitemap(settings)

        # Website administration
        self.configure_admin(settings)

        # Sessions and users
        self.configure_sessions(settings, _secrets)
        self.configure_user(settings, _secrets)
        self.configure_user_admin(settings)

        self.configure_notebook(settings)

        # Configure addons before anything else, so we can override bits from addon, like template lookup paths, later easily
        self.configure_addons()

        # Database
        # This must be run before configure_database() because SQLAlchemy will resolve @declared_attr and we must have config present by then
        self.configure_instrumented_models()
        self.configure_database(settings)

    def sanity_check(self):
        """Perform post-initialization sanity checks.

        This is run on every startup to check that the database table schema matches our model definitions. If there are un-run migrations this will bail out and do not let the problem to escalate later.
        """
        from websauna.system.model import sanitycheck
        from websauna.system.model.meta import Base
        from websauna.system.model.meta import create_dbsession
        from websauna.system.core import redis

        dbsession = create_dbsession(self.config.registry.settings)

        if not sanitycheck.is_sane_database(Base, dbsession):
            raise SanityCheckFailed("The database sanity check failed. Check log for details.")

        dbsession.close()

        if self._has_redis_sessions:
            if not redis.is_sane_redis(self.config):
                raise SanityCheckFailed("Could not connect to Redis server.\nWebsauna is configured to use Redis server for session data.\nIt cannot start up without a running Redis server.\nPlease consult your operating system community how to install and start a Redis server.")

    def wrap_wsgi_app(self, app):
        """Perform any necessary WSGI application wrapping.

        Wrap WSGI application to another WSGI application e.g. for the monitoring support. By default support New Relic.
        """

        if "NEW_RELIC_CONFIG_FILE" in os.environ:
            # Wrap for New Relic
            # libgcc_s.so.1 must be installed for pthread_cancel to work
            import newrelic.agent
            return newrelic.agent.wsgi_application()(app)

        return app

    def make_wsgi_app(self, sanity_check=True):
        """Create WSGI application from the current setup.

        :param sanity_check: True if perform post-initialization sanity checks.
        :return: WSGI application
        """
        app = self.config.make_wsgi_app()
        # Carry the initializer around so we can access it in tests

        app.initializer = self

        if "sanity_check" in self.global_config:
            # Command line scripts can override this when calling bootstrap()
            sanity_check = self.global_config["sanity_check"]
        else:
            sanity_check = asbool(self.settings.get("websauna.sanity_check", True))

        if sanity_check:
            self.sanity_check()

        app = self.wrap_wsgi_app(app)

        return app


def get_init(global_config, settings, init_cls=None):
    """Get Initializer class instance for WSGI-like app.

    TODO: Deprecated. Use Pyramid's ``bootstrap()`` instead.

    Reads reference to the initializer from settings, resolves it and creates the initializer instance.

    Example 1::

        config_uri = argv[1]
        init = get_init(dict(__file__=config_uri), settings)

    :param global_config: Global config dictionary, having __file__ entry as given by Paster

    :param settings: Settings dictionary

    :param init_cls: Explicitly give the Initializer class to use, otherwise read ``websauna.init`` settings.
    """

    assert "websauna.init" in settings, "You must have websauna.init setting pointing to your Initializer class"

    assert "__file__" in global_config

    if not init_cls:
        init_cls = settings.get("websauna.init")
        if not init_cls:
            raise RuntimeError("INI file lacks websauna.init option")
        resolver = DottedNameResolver()
        init_cls = resolver.resolve(init_cls)
    init = init_cls(global_config, settings)
    return init


def main(global_config, **settings):
    """Entry point for creating a Pyramid WSGI application."""

    init = Initializer(global_config)
    init.run()

    wsgi_app = init.make_wsgi_app()

    return wsgi_app
