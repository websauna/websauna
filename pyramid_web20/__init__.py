import configparser
import os

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.path import DottedNameResolver

from sqlalchemy import engine_from_config

from pyramid_mailer.interfaces import IMailer
from pyramid.settings import aslist

from . import views
from .utils import configinclude
from .utils import dictutil
from . import models
from . import authomatic
from . import auth
from . import admin


class Initializer:
    """Initialize various subsystems and routes.

    Customizers can subclass this and override parts they want to change.
    """
    def __init__(self, settings):

        # XXX: Side effect here for stupid config workaround -> fix with sensible API
        configinclude.augment(settings)

        self.config = Configurator(settings=settings)

        #: Declarative base for Horus models
        self.AuthBase = None

        #: SQLAlchemy engine
        self.engine = None

        #: Python module which provides Horus models
        self.user_models_module = None

        self.settings = settings

    def configure_user_model(self, settings):
        return settings

    def configure_horus(self, settings):

        # Avoid importing horus if not needed as it will bring in its own SQLAlchemy models and dirties our SQLAlchemy initialization
        from hem.interfaces import IDBSession
        from . import schemas
        from . import models
        from . import auth
        from horus.interfaces import IRegisterSchema
        from horus.interfaces import ILoginSchema

        # Tell horus which SQLAlchemy scoped session to use:
        registry = self.config.registry
        registry.registerUtility(models.DBSession, IDBSession)

        resolver = DottedNameResolver()
        self.user_models_module = users_models = resolver.resolve(settings["pyramid_web20.user_models_module"])

        self.config.include('horus')
        self.config.scan_horus(users_models)

        self.config.add_route('waiting_for_activation', '/waiting-for-activation')
        self.config.add_route('registration_complete', '/registration-complete')
        self.config.registry.registerUtility(schemas.RegisterSchema, IRegisterSchema)
        self.config.registry.registerUtility(schemas.LoginSchema, ILoginSchema)

        self.config.add_request_method(auth.get_user, 'user', reify=True)

        # Pass the declarateive base for user models
        return users_models.Base

    def configure_mailer(self, settings):
        """Configure outgoing email backend based on the INI settings."""

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

        # Jinja 2 templates as .html files
        self.config.include('pyramid_jinja2')
        self.config.add_jinja2_renderer('.html')
        self.config.add_jinja2_renderer('.txt')
        self.config.add_jinja2_search_path('pyramid_web20:templates', name='.html')
        self.config.add_jinja2_search_path('pyramid_web20:templates', name='.txt')

        self.config.include("pyramid_web20.views.templatecontext")

    def configure_authentication(self, settings, secrets):

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

        engine = engine_from_config(settings, 'sqlalchemy.')
        models.DBSession.configure(bind=engine)
        return engine

    def configure_views(self, settings):
        self.config.add_route('home', '/')
        self.config.scan(views)

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
        _admin = admin.Admin()
        self.config.registry.settings["pyramid_web20.admin"] = _admin

    def configure_admin(self, settings):
        """Configure admin interface."""
        self.config.add_route('admin', '/admin', factory=admin.Admin.admin_root_factory)
        self.config.add_route('admin_model', '/admin/{model}')

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

        # This must go first, as we need to make sure all models are attached to Base
        self.configure_user_model(settings)
        self.AuthBase = self.configure_horus(settings)
        self.engine = self.configure_database(settings)
        self.configure_templates()
        self.configure_static(settings)
        self.configure_authentication(settings, secrets)
        self.configure_mailer(settings)
        self.configure_authomatic(settings, secrets)
        self.configure_views(settings)
        self.configure_sessions(settings, secrets)
        self.configure_admin(settings)
        self.configure_admin_models(settings)

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
