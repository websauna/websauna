"""Websauna framework initialization."""
import logging
import os

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.interfaces import IDebugLogger
from pyramid.path import DottedNameResolver
from pyramid.settings import aslist
from pyramid.settings import asbool

from sqlalchemy import engine_from_config
from pyramid_mailer.interfaces import IMailer
from pyramid_deform import configure_zpt_renderer

from websauna.system.model import Base
from websauna.system.model import DBSession
from websauna.system.user.interfaces import IUserClass, IGroupClass
from websauna.utils.configincluder import IncludeAwareConfigParser
from websauna.utils import dictutil


class SanityCheckFailed(Exception):
    """Looks like the application has configuration which would fail to run."""


class Initializer:
    """Initialize various subsystems and routes.

    Customizers can subclass this and override parts they want to change.
    """
    def __init__(self, global_config, settings):

        #: This is the reference to the config file which started our process. We need to later pass it to Notebook.
        settings["websauna.global_config"] = global_config
        self.global_config = global_config

        self.config = self.create_configurator(settings)

        #: SQLAlchemy engine
        self.engine = None

        #: Python module which provides Horus models
        self.user_models_module = None

        self.settings = settings

    def create_configurator(self, settings):
        """Create configurator instance."""
        configurator = Configurator(settings=settings)
        return configurator

    def configure_logging(self, settings):
        """Create and set Pyramid debug logger.

        Please note that most o the logging is configured through the configuration file and that should be the primary way to do it.
        """

        # Make sure we can target Pyramid router debug messages in logging configuration
        pyramid_debug_logger = logging.getLogger("pyramid_debug")
        self.config.registry.registerUtility(pyramid_debug_logger, IDebugLogger)

    def configure_horus(self, settings):

        # Avoid importing horus if not needed as it will bring in its own SQLAlchemy models and dirties our SQLAlchemy initialization
        from hem.interfaces import IDBSession
        from websauna.system.user import schemas
        from websauna.system.user import auth
        from horus.interfaces import IRegisterSchema
        from horus.interfaces import ILoginSchema
        from horus.resources import UserFactory
        from websauna.system.user import horus as horus_init
        from horus import IResetPasswordSchema

        # Tell horus which SQLAlchemy scoped session to use:
        registry = self.config.registry
        registry.registerUtility(DBSession, IDBSession)

        resolver = DottedNameResolver()
        self.user_models_module = users_models = resolver.resolve(settings["websauna.user_models_module"])

        # Mark activate user and group class
        registry.registerUtility(users_models.User, IUserClass)
        registry.registerUtility(users_models.Group, IGroupClass)

        # self.config.include("horus")
        horus_init.includeme(self.config)

        self.config.scan_horus(users_models)

        self.config.add_route('waiting_for_activation', '/waiting-for-activation')
        self.config.add_route('registration_complete', '/registration-complete')
        self.config.add_route('login', '/login')
        self.config.add_route('logout', '/logout')
        self.config.add_route('forgot_password', '/forgot-password')
        self.config.add_route('reset_password', '/reset-password/{code}')
        self.config.add_route('register', '/register')
        self.config.add_route('activate', '/activate/{user_id}/{code}', factory=UserFactory)
        self.config.registry.registerUtility(schemas.RegisterSchema, IRegisterSchema)
        self.config.registry.registerUtility(schemas.LoginSchema, ILoginSchema)
        self.config.registry.registerUtility(schemas.ResetPasswordSchema, IResetPasswordSchema)

        self.config.add_request_method(auth.get_user, 'user', reify=True)

        # Pass the declarateive base for user models
        return users_models.Base

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

        # Some Horus templates need still Mako in place - TODO: remove this when all templates are converted
        self.config.include('pyramid_mako')

        self.config.include("websauna.system.core.templatecontext")

        def include_filter(name, func):

            def deferred():
                for renderer_name in (".html", ".txt"):
                    env = self.config.get_jinja2_environment(name=renderer_name)
                    assert env, "Jinja 2 not configured - cannot add filters"
                    env.filters[name] = func

            # Because Jinja 2 engine is not initialized here, only included here, we need to do template filter including asynchronously
            self.config.action('pyramid_web-include-filter-{}'.format(name), deferred, order=1)

        include_filter("friendly_time", templatecontext.friendly_time)
        include_filter("datetime", templatecontext.filter_datetime)
        include_filter("escape_js", templatecontext.escape_js)
        include_filter("timestruct", templatecontext.timestruct)

        # Make Deform widgets aware of our widget template paths
        configure_zpt_renderer(["websauna:system/form/templates/deform"])

        # Add core templates to the search path
        self.config.add_jinja2_search_path('websauna.system:core/templates', name='.html')
        self.config.add_jinja2_search_path('websauna.system:core/templates', name='.txt')

    def configure_authentication(self, settings, secrets):

        from websauna.system.user import auth

        # Security policies
        authn_policy = AuthTktAuthenticationPolicy(secrets['authentication.secret'], callback=auth.find_groups, hashalg='sha512')
        authz_policy = ACLAuthorizationPolicy()
        self.config.set_authentication_policy(authn_policy)
        self.config.set_authorization_policy(authz_policy)

    def configure_panels(self, settings):
        self.config.include('pyramid_layout')

    def configure_authomatic(self, settings, secrets):
        """Configure Authomatic social logins.

        Read enabled logins from the configuration file.

        Read consumer secrets from a secrets.ini.
        """
        from websauna.system.user import authomatic

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

        authomatic.setup(authomatic_secret, authomatic_config)

    def configure_database(self, settings):
        """
        :param settings: Any individual settings to override.

        :return: SQLEngine instance
        """
        from websauna.system.model import DBSession

        settings = dictutil.combine(self.settings, settings)
        # http://stackoverflow.com/questions/14783505/encoding-error-with-sqlalchemy-and-postgresql
        engine = engine_from_config(settings, 'sqlalchemy.', connect_args={"options": "-c timezone=utc"}, client_encoding='utf8')
        DBSession.configure(bind=engine)
        return engine

    def configure_instrumented_models(self, settings):
        """Configure models from third party addons.

        Third party addons might need references to configurable models which are not available at the import time. One of these models is user - you can supply your own user model. However third party addon models might want to build foreign key relationships to this model. Thus, ``configure_instrumented_models()`` is an initialization step which is called when database setup is half way there and you want to throw in some extra models in.
        """

        # Expose Pyramid configuration to classes
        Base.metadata.pyramid_config = self.config

    def configure_error_views(self, settings):

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
            self.config.add_route('error_trigger', '/error-trigger')

    def configure_root(self):
        """Root object defines permissions for route URLs which have not their own traversing context.

        http://pyramid-tutorials.readthedocs.org/en/latest/getting_started/10-security/
        """
        from websauna.system.core.root import Root
        self.config.set_root_factory(Root.root_factory)

    def configure_views(self, settings):
        from websauna.system.core.views import home
        self.config.add_route('home', '/')
        self.config.scan(home)

    def configure_static(self, settings):
        """Configure static media serving and cache busting.

        http://docs.pylonsproject.org/projects/pyramid/en/1.6-branch/narr/assets.html#static-assets-section
        """
        cachebust = asbool(self.settings.get("websauna.cachebust"))
        self.config.add_static_view('static', 'websauna:static', cachebust=cachebust)

    def configure_sessions(self, settings, secrets):
        """Configure session storage."""

        session_secret = secrets["session.secret"]

        # TODO: Make more boilerplate here so that we pass secret in more sane way
        self.config.registry.settings["redis.sessions.secret"] = session_secret

        self.config.include("pyramid_redis_sessions")

    def configure_admin_models(self, settings):
        """Configure CRUD for known SQLAlchemy models."""

    def preconfigure_admin(self, settings):
        # Register admin root object
        from websauna.system.admin import Admin
        _admin = Admin()
        self.config.registry.settings["websauna.admin"] = _admin

    def configure_admin(self, settings):
        """Configure admin interface."""

        from websauna.system.admin import views

        self.config.add_jinja2_search_path('websauna.system.admin:templates', name='.html')
        self.config.add_jinja2_search_path('websauna.system.admin:templates', name='.txt')

        self.config.add_route('admin_home', '/admin/', factory="websauna.system.admin.admin_root_factory")
        self.config.add_route('admin', "/admin/*traverse", factory="websauna.system.admin.admin_root_factory")

        self.config.add_panel('websauna.system.admin.views.default_model_admin_panel')
        # self.config.add_view('websauna.system.admin.views.listing', context='websauna.system.admin.ModelAdmin')
        # self.config.add_view('websauna.system.admin.views.panel', context='websauna.system.admin.AdminPanel')
        self.config.scan(views)

        # Add templatecontext handler
        from websauna.system.admin import templatecontext
        templatecontext.includeme(self.config)

    def preconfigure_user(self, settings):
        # self.configure_horus(settings)
        pass

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

    def configure_user(self, settings, secrets):
        """Configure user model, sign in and sign up subsystem."""
        from websauna.system.user import views

        self.configure_authentication(settings, secrets)
        self.configure_authomatic(settings, secrets)

        # XXX: Different syntax to include templates as with admin... circular import problem, etc?
        self.config.add_jinja2_search_path('websauna.system:user/templates', name='.html')
        self.config.add_jinja2_search_path('websauna.system:user/templates', name='.txt')

        self.config.scan(views)

        # TODO: Horus implicitly imports its admin views... WE DON'T WANT THOSE and we cannot avoid import for now.
        # Thus, do Horus import as last.
        # Long term solution: Work with the upstream to fix Horus behavior.
        self.configure_horus(settings)

    def configure_user_admin(self, settings):
        import websauna.system.user.admin
        import websauna.system.user.adminviews
        from websauna.system.admin import Admin

        _admin = Admin.get_admin(self.config.registry)
        _admin.scan(self.config, websauna.system.user.admin)
        self.config.scan(websauna.system.user.adminviews)

    def configure_notebook(self, settings):
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
        """Configure Celery.

        """

        # Patch pyramid_celery to use our config loader
        import websauna.system.celery

        # Patch various paster internals
        from websauna.utils.configincluder import monkey_patch_paster_config_parser
        monkey_patch_paster_config_parser()
        self.config.include("pyramid_celery")

        self.config.configure_celery(self.global_config["__file__"])

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

    def run(self, settings):
        _secrets = self.read_secrets(settings)

        self.configure_logging(settings)

        self.preconfigure_user(settings)
        self.preconfigure_admin(settings)
        self.configure_forms(settings)

        # Serving
        self.configure_templates()
        self.configure_static(settings)

        # Email
        self.configure_mailer(settings)

        # Timed tasks
        self.configure_scheduler(settings)
        self.configure_tasks(settings)

        # Core view and layout related
        self.configure_root()
        self.configure_error_views(settings)
        self.configure_views(settings)
        self.configure_panels(settings)

        # Sessions and users
        self.configure_sessions(settings, _secrets)
        self.configure_user(settings, _secrets)
        self.configure_user_admin(settings)
        self.configure_crud(settings)

        # Website administration
        self.configure_admin(settings)
        self.configure_admin_models(settings)
        self.configure_notebook(settings)

        self.configure_instrumented_models(settings)
        self.engine = self.configure_database(settings)

    def sanity_check(self):
        """Perform post-initialization sanity checks.
        """
        from websauna.system.model import sanitycheck
        if not sanitycheck.is_sane_database(Base, DBSession):
            raise SanityCheckFailed("The database sanity check failed. Check log for details.")

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
    """ This function returns a Pyramid WSGI application.
    """

    settings = IncludeAwareConfigParser.retrofit_settings(global_config)
    init = Initializer(global_config, settings)
    init.run(settings)

    wsgi_app = init.make_wsgi_app()

    return wsgi_app
