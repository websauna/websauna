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


def configure_horus(config):
    # Tell horus which SQLAlchemy scoped session to use:
    from hem.interfaces import IDBSession
    registry = config.registry
    registry.registerUtility(models.DBSession, IDBSession)

    config.include('horus')
    config.scan_horus(models)

    #config.add_view('horus.views.AuthController', attr='login', route_name='login', renderer='login/login.html')
    #config.add_view('horus.views.RegisterController', attr='register', route_name='register', renderer='login/register.html')
    config.add_route('waiting_for_activation', '/waiting-for-activation')
    config.add_route('registration_complete', '/registration-complete')
    config.registry.registerUtility(schemas.RegisterSchema, IRegisterSchema)
    config.registry.registerUtility(schemas.LoginSchema, ILoginSchema)

    config.add_request_method(auth.get_user, 'user', reify=True)


def configure_mailer(config, settings):
    """Configure outgoing email backend based on the INI settings."""
    resolver = DottedNameResolver()
    mailer_cls = resolver.resolve(settings["pyramid_web20.mailer"])
    mailer = mailer_cls()

    config.registry.registerUtility(mailer, IMailer)


def configure_templates(config):

    # Jinja 2 templates as .html files
    config.include('pyramid_jinja2')
    config.add_jinja2_renderer('.html')
    config.add_jinja2_renderer('.txt')
    config.add_jinja2_search_path('pyramid_web20:templates', name='.html')
    config.add_jinja2_search_path('pyramid_web20:templates', name='.txt')

    config.include("pyramid_web20.views.templatecontext")


def configure_authentication(config, settings, secrets):

    # Security policies
    authn_policy = AuthTktAuthenticationPolicy(secrets['authentication']['secret'], callback=auth.find_groups, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)


def configure_authomatic(config, settings, secrets):
    """Configure Authomatic social logins.

    Read enabled logins from the configuration file.

    Read consumer secrets from a secrets.ini.
    """
    config.add_route('login_social', '/login/{provider_name}')

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


def read_secrets(settings):
    """Read secrets configuration file.

    Stores API keys, such.
    """

    # Secret configuration diretives
    secrets_file = settings.get("pyramid_web20.secrets_file")
    if not secrets_file:
        return {}

    config = configparser.ConfigParser()
    config.read(secrets_file)

    return config


# Done by Horus already?
# def configure_auth(config):
#     config.add_request_method(request.augment_request_get_user, 'user', reify=True)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    secrets = read_secrets(settings)

    engine = engine_from_config(settings, 'sqlalchemy.')
    models.DBSession.configure(bind=engine)
    models.Base.metadata.bind = engine
    config = Configurator(settings=settings)

    configure_templates(config)

    config.add_static_view('static', 'static', cache_max_age=3600)

    configure_authentication(config, settings, secrets)
    configure_horus(config)
    configure_mailer(config, settings)
    configure_authomatic(config, settings, secrets)

    config.add_route('home', '/')
    config.scan()
    config.scan(views)

    return config.make_wsgi_app()
