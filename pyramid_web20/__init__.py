import configparser
import os

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.path import DottedNameResolver

from sqlalchemy import engine_from_config

from pyramid_mailer.interfaces import IMailer
from pyramid.settings import aslist
from pyramid.settings import asbool

from .utils import configinclude
from .utils import dictutil
from . import models
from .models import DBSession
from .system.user import authomatic
from .system.admin import Admin


class Initializer:
    """Initialize various subsystems and routes.

    Customizers can subclass this and override parts they want to change.
    """
    def __init__(self, settings):

        # XXX: Side effect here for stupid config workaround -> fix with sensible API
        configinclude.augment(settings)

        self.config = Configurator(settings=settings)

        #: SQLAlchemy engine
        self.engine = None

        #: Python module which provides Horus models
        self.user_models_module = None

        self.settings = settings

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

        # self.config.include("horus")
        horus_init.includeme(self.config)

        self.config.scan_horus(users_models)

        self.config.add_route('waiting_for_activation', '/waiting-for-activation')
        self.config.add_route('registration_complete', '/registration-complete')
        self.config.add_route('login', '/login')
        self.config.add_route('logout', '/logout')
        self.config.add_route('register', '/register')
        self.config.add_route('activate', '/activate/{user_id}/{code}', factory=UserFactory)
        self.config.registry.registerUtility(schemas.RegisterSchema, IRegisterSchema)
        self.config.registry.registerUtility(schemas.LoginSchema, ILoginSchema)

        self.config.add_request_method(auth.get_user, 'user', reify=True)

        # Pass the declarateive base for user models
        return users_models.Base

    def configure_mailer(self, settings):
        """Configure outgoing email backend based on the INI settings."""

        settings = settings.copy()

        # Empty values are not handled gracefully, so remove them before passing forward to mailer
        if settings.get("mail.username", "x") == "":
            del settings["mail.username"]

        if settings.get("mail.password", "x") == "":
            del settings["mail.password"]

        mailer_class = settings.get("pyramid_web20.mailer", "")
        if mailer_class in ("mail", ""):
            # TODO: Make mailer_class explicit so we can dynamically load pyramid_mail.Mailer
            # Default
            from pyramid_mailer import mailer_factory_from_settings
            mailer_factory_from_settings(settings)
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
        self.config.add_jinja2_search_path('pyramid_web20:system/core/templates', name='.html')
        self.config.add_jinja2_search_path('pyramid_web20:system/core/templates', name='.txt')

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

    def configure_authentication(self, settings, secrets):

        from .system.user import auth

        # Security policies
        authn_policy = AuthTktAuthenticationPolicy(secrets['authentication']['secret'], callback=auth.find_groups, hashalg='sha512')
        authz_policy = ACLAuthorizationPolicy()
        self.config.set_authentication_policy(authn_policy)
        self.config.set_authorization_policy(authz_policy)

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

        authomatic_secret = secrets["authomatic"]["secret"]

        resolver = DottedNameResolver()

        for login in social_logins:

            if login not in secrets.sections():
                raise RuntimeError("Secrets configuration file missing or missing the [{}] section".format(login))

            authomatic_config[login] = {}
            authomatic_config[login]["consumer_key"] = secrets.get(login, "consumer_key")
            authomatic_config[login]["consumer_secret"] = secrets.get(login, "consumer_secret")
            authomatic_config[login]["scope"] = aslist(secrets.get(login, "scope"))
            authomatic_config[login]["class_"] = resolver.resolve(secrets.get(login, "class"))

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

    def configure_views(self, settings):
        from .system.core.views import home
        self.config.add_route('home', '/')
        self.config.scan(home)

        # Forbidden view overrides helpful auth debug error messages,
        # so pull in only when really needed
        if not asbool(settings["pyramid.debug_authorization"]):
            from .system.core.views import forbidden
            self.config.scan(forbidden)

    def configure_static(self, settings):
        self.config.add_static_view('static', 'static', cache_max_age=3600)

    def configure_sessions(self, settings, secrets):
        """Configure session storage."""

        session_secret = secrets["session"]["secret"]

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

        # self.config.add_view('pyramid_web20.system.admin.views.listing', context='pyramid_web20.system.admin.ModelAdmin')
        # self.config.add_view('pyramid_web20.system.admin.views.panel', context='pyramid_web20.system.admin.AdminPanel')

        self.config.scan(views)


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

    def read_secrets(self, settings):
        """Read secrets configuration file.

        Stores API keys, such.
        """

        # Secret configuration diretives
        secrets_file = settings.get("pyramid_web20.secrets_file")
        if not secrets_file:
            return {}

        if not os.path.exists(secrets_file):
            p = os.path.abspath(secrets_file)
            raise RuntimeError("Secrets file {} missing".format(p))

        secrets_config = configparser.ConfigParser()
        secrets_config.read(secrets_file)

        return secrets_config

    def run(self, settings):
        secrets = self.read_secrets(settings)

        self.preconfigure_user(settings)
        self.preconfigure_admin(settings)

        self.configure_templates()
        self.configure_static(settings)
        self.configure_mailer(settings)

        self.configure_views(settings)
        self.configure_sessions(settings, secrets)

        self.configure_user(settings, secrets)
        self.configure_user_admin(settings)
        self.configure_crud(settings)

        self.configure_admin(settings)
        self.configure_admin_models(settings)

        # This must go first, as we need to make sure all models are attached to Base
        self.engine = self.configure_database(settings)

    def make_wsgi_app(self):
        return self.config.make_wsgi_app()


def get_init(settings):
    """Return instance of Initializer for the app."""

    assert "pyramid_web20.init" in settings, "You must have pyramid_web20.init setting pointing to your Initializer class"

    init_cls = settings.get("pyramid_web20.init")
    if not init_cls:
        raise RuntimeError("INI file lacks pyramid_web20.init optoin")
    resolver = DottedNameResolver()
    init_cls = resolver.resolve(init_cls)
    init = init_cls(settings)
    return init


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    init = Initializer(settings)
    init.run(settings)
    return init.make_wsgi_app()
