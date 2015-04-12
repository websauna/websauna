from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.path import DottedNameResolver

from sqlalchemy import engine_from_config

from pyramid_mailer.interfaces import IMailer
from .mail import StdoutMailer

from . import models
from . import views
from . import schemas
from . import auth

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


def configure_authentication(config, settings):

    # Security policies
    authn_policy = AuthTktAuthenticationPolicy(settings['pyramid_web20.authenication_secret'], callback=auth.find_groups, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)


# Done by Horus already?
# def configure_auth(config):
#     config.add_request_method(request.augment_request_get_user, 'user', reify=True)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    models.DBSession.configure(bind=engine)
    models.Base.metadata.bind = engine
    config = Configurator(settings=settings)

    configure_templates(config)

    config.add_static_view('static', 'static', cache_max_age=3600)

    configure_authentication(config, settings)
    configure_horus(config)
    configure_mailer(config, settings)

    config.add_route('home', '/')
    config.scan()
    config.scan(views)

    return config.make_wsgi_app()
