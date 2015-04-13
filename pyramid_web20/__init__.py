import configparser

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.path import DottedNameResolver

from sqlalchemy import engine_from_config

from pyramid_mailer.interfaces import IMailer
from pyramid.settings import aslist

from . import models
from . import views
from . import schemas
from . import auth

from . import authomatic

from horus.interfaces import IRegisterSchema
from horus.interfaces import ILoginSchema


class Initializer:
    """Initialize various subsystems and routes.

    Customizers can subclass this and override parts they want to change.
    """
    def __init__(self, settings):
        self.config = Configurator(settings=settings)

    def configure_horus(self):
        # Tell horus which SQLAlchemy scoped session to use:
        from hem.interfaces import IDBSession
        registry = self.config.registry
        registry.registerUtility(models.DBSession, IDBSession)

        self.config.include('horus')
        self.config.scan_horus(models)

        #self.config.add_view('horus.views.AuthController', attr='login', route_name='login', renderer='login/login.html')
        #self.config.add_view('horus.views.RegisterController', attr='register', route_name='register', renderer='login/register.html')
        self.config.add_route('waiting_for_activation', '/waiting-for-activation')
        self.config.add_route('registration_complete', '/registration-complete')
        self.config.registry.registerUtility(schemas.RegisterSchema, IRegisterSchema)
        self.config.registry.registerUtility(schemas.LoginSchema, ILoginSchema)

        self.config.add_request_method(auth.get_user, 'user', reify=True)

    def configure_mailer(self, settings):
        """Configure outgoing email backend based on the INI settings."""
        resolver = DottedNameResolver()
        mailer_cls = resolver.resolve(settings["pyramid_web20.mailer"])
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
        engine = engine_from_config(settings, 'sqlalchemy.')
        models.DBSession.configure(bind=engine)
        models.Base.metadata.bind = engine

    def configure_views(self, settings):
        self.config.add_route('home', '/')
        self.config.scan()
        self.config.scan(views)

    def configure_static(self, settings):
        self.config.add_static_view('static', 'static', cache_max_age=3600)

    def configure_sessions(self, settings, secrets):
        """Configure session storage."""

        session_secret = secrets["session"]["secret"]

        # TODO: Make more boilerplate here so that we pass secret in more sane way
        self.config.registry.settings["redis.sessions.secret"] = session_secret

        self.config.include("pyramid_redis_sessions")

    def read_secrets(self, settings):
        """Read secrets configuration file.

        Stores API keys, such.
        """

        # Secret configuration diretives
        secrets_file = settings.get("pyramid_web20.secrets_file")
        if not secrets_file:
            return {}

        secrets_config = configparser.ConfigParser()
        secrets_config.read(secrets_file)

        return secrets_config

    def run(self, settings):
        secrets = self.read_secrets(settings)

        self.configure_database(settings)
        self.configure_templates()
        self.configure_static(settings)
        self.configure_authentication(settings, secrets)
        self.configure_horus()
        self.configure_mailer(settings)
        self.configure_authomatic(settings, secrets)
        self.configure_views(settings)
        self.configure_sessions(settings, secrets)

    def make_wsgi_app(self):
        return self.config.make_wsgi_app()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    init = Initializer(settings)
    init.run(settings)
    return init.make_wsgi_app()
