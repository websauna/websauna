import configparser
import logging
import subprocess
from horus import IResetPasswordSchema
import os

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.interfaces import IDebugLogger
from pyramid.path import DottedNameResolver
from pyramid_deform import configure_zpt_renderer
from pyramid_web20.system.core import secrets
from pyramid_web20.system.model import Base
from pyramid_web20.system.model import DBSession
from pyramid_web20.system.user.interfaces import IUserClass, IGroupClass
from pyramid_web20.utils.configincluder import IncludeAwareConfigParser

from sqlalchemy import engine_from_config

from pyramid_mailer.interfaces import IMailer
from pyramid.settings import aslist
from pyramid.settings import asbool

from .utils import dictutil
from . import models
from .system.user import authomatic
from .system.admin import Admin


class SanityCheckFailed(Exception):
    """Looks like the application has configuration which would fail to run."""


class Initializer:
    """Initialize various subsystems and routes.

    Customizers can subclass this and override parts they want to change.
    """
    def __init__(self, global_config, settings):

        #: This is the reference to the config file which started our process. We need to later pass it to Notebook.
        settings["pyramid_web20.global_config"] = global_config
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
        from .system.user import schemas
        from .system.user import auth
        from horus.interfaces import IRegisterSchema
        from horus.interfaces import ILoginSchema
        from horus.resources import UserFactory
        from .system.user import horus as horus_init

        # Tell horus which SQLAlchemy scoped session to use:
        registry = self.config.registry
        registry.registerUtility(DBSession, IDBSession)

        resolver = DottedNameResolver()
        self.user_models_module = users_models = resolver.resolve(settings["pyramid_web20.user_models_module"])

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

        mailer_class = settings.get("pyramid_web20.mailer", "")
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
        from pyramid_web20.system.core import templatecontext

        # Jinja 2 templates as .html files
        self.config.include('pyramid_jinja2')
        self.config.add_jinja2_renderer('.html')
        self.config.add_jinja2_renderer('.txt')
        self.config.add_jinja2_renderer('.css')

        # Some Horus templates need still Mako in place - TODO: remove this when all templates are converted
        self.config.include('pyramid_mako')

        self.config.include("pyramid_web20.system.core.templatecontext")

        def include_filter(name, func):

            def deferred():
                for renderer_name in (".html", ".txt"):
                    env = self.config.get_jinja2_environment(name=renderer_name)
                    assert env, "Jinja 2 not configured - cannot add filters"
                    env.filters[name] = func

            # Because Jinja 2 engine is not initialized here, only included here, we need to do template filter including asynchronously
            self.config.action('pyramid_web-include-filter-{}'.format(name), deferred, order=1)

        include_filter("friendly_time", templatecontext.friendly_time)
        include_filter("datetime", templatecontext._datetime)
        include_filter("escape_js", templatecontext.escape_js)
        include_filter("timestruct", templatecontext.timestruct)

        # Make Deform widgets aware of our widget template paths
        configure_zpt_renderer(["pyramid_web20:system/form/templates/deform"])

        # Add core templates to the search path
        self.config.add_jinja2_search_path('pyramid_web20:system/core/templates', name='.html')
        self.config.add_jinja2_search_path('pyramid_web20:system/core/templates', name='.txt')

    def configure_authentication(self, settings, secrets):

        from .system.user import auth

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
        self.config.add_route('login_social', '/login/{provider_name}')

        social_logins = aslist(settings.get("pyramid_web20.social_logins", ""))

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
        settings = dictutil.combine(self.settings, settings)
        # http://stackoverflow.com/questions/14783505/encoding-error-with-sqlalchemy-and-postgresql
        engine = engine_from_config(settings, 'sqlalchemy.', connect_args={"options": "-c timezone=utc"},  client_encoding='utf8')
        models.DBSession.configure(bind=engine)
        return engine

    def configure_error_views(self, settings):

        # Forbidden view overrides helpful auth debug error messages,
        # so pull in only when really needed
        if not asbool(settings["pyramid.debug_authorization"]):
            from .system.core.views import forbidden
            self.config.scan(forbidden)

        if not asbool(settings["pyramid.debug_notfound"]):
            from .system.core.views import notfound
            self.config.scan(notfound)

        # Internal server error must be only activated in the production mode, as it clashes with pyramid_debugtoolbar
        if "pyramid_debugtoolbar" not in aslist(settings["pyramid.includes"]):
            from .system.core.views import internalservererror
            self.config.scan(internalservererror)
            self.config.add_route('error_trigger', '/error-trigger')

    def configure_root(self):
        """Root object defines permissions for route URLs which have not their own traversing context.

        http://pyramid-tutorials.readthedocs.org/en/latest/getting_started/10-security/
        """
        from pyramid_web20.system.core.root import Root
        self.config.set_root_factory(Root.root_factory)

    def configure_views(self, settings):
        from .system.core.views import home
        self.config.add_route('home', '/')
        self.config.scan(home)

    def configure_static(self, settings):
        """Configure static media serving and cache busting.

        http://docs.pylonsproject.org/projects/pyramid/en/1.6-branch/narr/assets.html#static-assets-section
        """
        cachebust = asbool(self.settings.get("pyramid_web20.cachebust"))
        self.config.add_static_view('static', 'static', cachebust=cachebust)

    def configure_sessions(self, settings, secrets):
        """Configure session storage."""

        session_secret = secrets["session.secret"]

        # TODO: Make more boilerplate here so that we pass secret in more sane way
        self.config.registry.settings["redis.sessions.secret"] = session_secret

        self.config.include("pyramid_redis_sessions")

    def configure_admin_models(self, settings):
        """Configure CRUD for known SQLAlchemy models."""

        from .system.admin import views
        _admin = self.config.registry.settings["pyramid_web20.admin"]

    def preconfigure_admin(self, settings):
        # Register admin root object
        _admin = Admin()
        self.config.registry.settings["pyramid_web20.admin"] = _admin

    def configure_admin(self, settings):
        """Configure admin interface."""

        from pyramid_web20.system.admin import views

        self.config.add_jinja2_search_path('pyramid_web20.system.admin:templates', name='.html')
        self.config.add_jinja2_search_path('pyramid_web20.system.admin:templates', name='.txt')

        self.config.add_route('admin_home', '/admin/', factory="pyramid_web20.system.admin.admin_root_factory")
        self.config.add_route('admin', "/admin/*traverse", factory="pyramid_web20.system.admin.admin_root_factory")

        self.config.add_panel('pyramid_web20.system.admin.views.default_model_admin_panel')
        # self.config.add_view('pyramid_web20.system.admin.views.listing', context='pyramid_web20.system.admin.ModelAdmin')
        # self.config.add_view('pyramid_web20.system.admin.views.panel', context='pyramid_web20.system.admin.AdminPanel')
        self.config.scan(views)

        # Add templatecontext handler
        from pyramid_web20.system.admin import templatecontext
        templatecontext.includeme(self.config)

    def preconfigure_user(self, settings):
        # self.configure_horus(settings)
        pass

    def configure_crud(self, settings):
        """CRUD templates and views."""

        self.config.add_jinja2_search_path('pyramid_web20.system.crud:templates', name='.html')
        self.config.add_jinja2_search_path('pyramid_web20.system.crud:templates', name='.txt')

        from pyramid_web20.system.crud import views
        self.config.scan(views)

    def configure_user(self, settings, secrets):

        from .system.user import views

        self.configure_authentication(settings, secrets)
        self.configure_authomatic(settings, secrets)

        # XXX: Different syntax to include templates as with admin... circular import problem, etc?
        self.config.add_jinja2_search_path('pyramid_web20:system/user/templates', name='.html')
        self.config.add_jinja2_search_path('pyramid_web20:system/user/templates', name='.txt')

        self.config.scan(views)

        # TODO: Horus implicitly imports its admin views... WE DON'T WANT THOSE and we cannot avoid import for now.
        # Thus, do Horus import as last.
        # Long term solution: Work with the upstream to fix Horus behavior.
        self.configure_horus(settings)

    def configure_user_admin(self, settings):
        import pyramid_web20.system.user.admin
        import pyramid_web20.system.user.adminviews

        admin = Admin.get_admin(self.config.registry)
        admin.scan(self.config, pyramid_web20.system.user.admin)
        self.config.scan(pyramid_web20.system.user.adminviews)

    def configure_notebook(self, settings):
        import pyramid_web20.system.notebook.views
        self.config.add_route('admin_shell', '/notebook/admin-shell')
        self.config.add_route('shutdown_notebook', '/notebook/shutdown')
        self.config.add_route('notebook_proxy', '/notebook/*remainder')
        self.config.scan(pyramid_web20.system.notebook.views)

    def configure_tasks(self, settings):
        """Scan all Python modules with asynchoronou sna dperiodic tasks to be imported."""

        # Importing the task is enough to add it to Celerybeat working list
        from pyramid_web20.system.devops import tasks  # noqa


    def configure_scheduler(self, settings):
        """Configure Celery.

        """

        # Patch pyramid_celery to use our config loader
        import pyramid_web20.system.celery

        # Patch various paster internals
        from pyramid_web20.utils.configincluder import monkey_patch_paster_config_parser
        monkey_patch_paster_config_parser()
        self.config.include("pyramid_celery")

        self.config.configure_celery(self.global_config["__file__"])

    def read_secrets(self, settings):
        """Read secrets configuration file.

        Stores API keys, such.
        """
        # Secret configuration diretives
        secrets_file = settings.get("pyramid_web20.secrets_file")
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

        # This must go first, as we need to make sure all models are attached to Base
        self.engine = self.configure_database(settings)

    def sanity_check(self):
        """Perform post-initialization sanity checks.
        """
        from pyramid_web20.system.model import sanitycheck
        if not sanitycheck.is_sane_database(Base, DBSession):
            raise SanityCheckFailed("The database sanity check failed. Check log for details.")

    def make_wsgi_app(self, sanity_check=True):
        """Create WSGI application from the current setup.

        :param sanity_check: True if perform post-initialization sanity checks.
        :return: WSGI application
        """
        app = self.config.make_wsgi_app()
        # Carry the initializer around so we can access it in tests

        app.initializer = self

        if sanity_check:
            self.sanity_check()

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

    :param init_cls: Explicitly give the Initializer class to use, otherwise read ``pyramid_web20.init`` settings.
    """

    assert "pyramid_web20.init" in settings, "You must have pyramid_web20.init setting pointing to your Initializer class"

    assert "__file__" in global_config

    if not init_cls:
        init_cls = settings.get("pyramid_web20.init")
        if not init_cls:
            raise RuntimeError("INI file lacks pyramid_web20.init option")
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

    # Create application, skip sanity check if needed
    sanity_check = asbool(settings.get("pyramid_web20.sanity_check", True))
    wsgi_app = init.make_wsgi_app(sanity_check=sanity_check)

    return wsgi_app
