"""Websauna framework initialization routine."""

#
# NOTE: Be careful about not to import anything in this file head that might cause the import of `transaction` package. If Websauna is used with gevent async event loop and gevent monkey patches, the patching order would become incorrect. This is because importlib and setuptools autoscan all top level imports on the application startup and this order cannot be controlled. Thus, to make gevent work you must not import anything dbsession/tranaction related in the package main file to be on the safe side.
#
# This, and the reason that we can use component architecture and replace and disable framework parts in Initializer, are the driving factors of not to do module level imports here.
#

# Standard Library
import logging
import os
import sys
import typing as t
from distutils.version import LooseVersion

# Pyramid
from pyramid.config import Configurator
from pyramid.interfaces import IDebugLogger
from pyramid.interfaces import IRequest
from pyramid.path import DottedNameResolver
from pyramid.settings import asbool
from pyramid.settings import aslist

import pkg_resources

# Websauna
from websauna.utils.autoevent import event_source
from websauna.utils.config.includer import IncludeAwareConfigParser  # noQA


class SanityCheckFailed(Exception):
    """Looks like the application has configuration which would fail to run."""


class RequirementsFailed(Exception):
    """Websauna minimum requirements were not met."""


def check_python_pyramid_requirements() -> bool:
    """Check for Python and Pyramid requirements.

    :return: Boolean indicating if Python and Pyramid requirements are met.
    """
    error_msg = ''
    python_version = sys.version_info
    pyramid_version = tuple(LooseVersion(pkg_resources.get_distribution('pyramid').version).version)
    if python_version < (3, 5, 2):
        error_msg = 'Python 3.5.2 or newer is required to run Websauna.'
    elif pyramid_version < (1, 7):
        error_msg = 'Pyramid version 1.7 or newer required'
    if error_msg:
        raise RequirementsFailed(error_msg)
    return True


def _expandvars(value: t.Any) -> t.Any:
    processed = value
    if isinstance(value, dict):
        processed = expandvars_dict(value)
    elif isinstance(value, (str, bytes)):
        processed = os.path.expandvars(value)
    return processed


def expandvars_dict(settings: dict) -> dict:
    """Expand all environment variables in a settings dictionary.

    ref: http://stackoverflow.com/a/16446566
    :returns: Dictionary with settings
    """
    return {key: _expandvars(value) for key, value in settings.items()}


class Initializer:
    """Initializer is responsible to ramp up the frameworks and subsystems.

    There exist one ``Initializer`` instance which you create in your WSGI application constructor.

    * You subclass the default ``Initializer`` provider by Websauna

    * You override the methods for the parts where you want to customize the default Websauna behavior

    * You also need to include addons and other Pyramid package configurations. This is usually done by calling ``self.config.include("your_pyramid_package")``.

    * You can add your own application specific view initializations, like ``self.config.scan()`` for your application Python modules to register ``@view_config`` directives in those.

    See :py:meth:`websauna.system.Initializer.run` for linear initialization order.

    Aspect-oriented approach with :py:mod:`websauna.utils.aspect.event_source` is used to provide hooks for addons to participate initialization process.

    .. note ::

        We deliberate push imports inside methods, so that it is unlikely we'd have any import time side effects caused by some less elegant solutions, like gevent.
    """

    def __init__(self, global_config: dict, settings: t.Optional[dict]=None):
        """
        :param global_config: Dictionary as passed to WSGI entry point.

        :param settings: DEPRECATED. Extra settings as passed to WSGI entry point. TODO: How to handle these?
        """
        import plaster

        # Check if Python and Pyramid versions are the required
        check_python_pyramid_requirements()

        if not settings:
            config = global_config['__file__']
            if not config.startswith('ws://'):
                config = 'ws://{0}'.format(config)

            loader = plaster.get_loader(config)
            # Read [app] section
            settings = loader.get_settings('app:main')

        #: This is the refer    ence to the config file which started our process. We need to later pass it to Notebook.
        settings["websauna.global_config"] = global_config
        self.global_config = global_config

        #: Reference to Celery app instance
        self.celery = None

        self.settings = expandvars_dict(settings)

        self.config = self.create_configurator()

        self.config.registry.static_asset_policy = self.static_asset_policy = self.create_static_asset_policy()

        #: Flag to tell if we need to do sanity check for redis sessiosn
        self._has_redis_sessions = False

        #: This flag keeps state if the initializer has been run or not.
        self._already_run = False

        # Exposed Websauna features
        self.config.registry.features = set()

        # Secrets file
        self.secrets = self.read_secrets()

    def create_configurator(self) -> Configurator:
        """Create Pyramid Configurator instance."""
        configurator = Configurator(settings=self.settings)

        # This is passed to addons
        configurator.registry.initializer = self
        return configurator

    def create_static_asset_policy(self):
        """Override to have our own static asset policy."""
        from websauna.system.http.static import DefaultStaticAssetPolicy
        return DefaultStaticAssetPolicy(self.config)

    def configure_logging(self):
        """Create and set Pyramid debug logger.

        Please note that most o the logging is configured through the configuration file and that should be the primary way to do it.
        """

        # Extract logging configuration from INI
        # from websauna.utils.configincluder import setup_logging

        # setup_logging(self.global_config["__file__"])

        # Make sure we can target Pyramid router debug messages in logging configuration
        pyramid_debug_logger = logging.getLogger("pyramid_debug")
        self.config.registry.registerUtility(pyramid_debug_logger, IDebugLogger)

    @event_source
    def configure_user_forms(self):
        """Configure forms and schemas used for login and such.

        :ref:`See documentation example <customize-user-form>`.
        """

        from websauna.system.user import interfaces
        from websauna.system.user import schemas
        from websauna.system.user.forms import DefaultUserForm
        from websauna.system.user.forms import DefaultLoginForm
        from websauna.system.user.forms import DefaultRegisterForm

        self.config.registry.registerUtility(schemas.RegisterSchema, interfaces.IRegisterSchema)
        self.config.registry.registerUtility(schemas.LoginSchema, interfaces.ILoginSchema)
        self.config.registry.registerUtility(schemas.ResetPasswordSchema, interfaces.IResetPasswordSchema)
        self.config.registry.registerUtility(schemas.ForgotPasswordSchema, interfaces.IForgotPasswordSchema)

        self.config.registry.registerUtility(DefaultLoginForm, interfaces.ILoginForm)
        self.config.registry.registerUtility(DefaultRegisterForm, interfaces.IRegisterForm)
        self.config.registry.registerUtility(DefaultUserForm, interfaces.IForgotPasswordForm)
        self.config.registry.registerUtility(DefaultUserForm, interfaces.IResetPasswordForm)

    @event_source
    def configure_mailer(self):
        """Configure outgoing email backend and email test views."""
        from pyramid_mailer import IMailer
        from websauna.system.mail.utils import create_mailer

        # TODO: There is upstrean issue in pyramid_mailer, see send_template_mail.
        # mailer gets created again
        mailer = create_mailer(self.config.registry)
        self.config.registry.registerUtility(mailer, IMailer)

        if self.config.registry.settings.get("websauna.sample_html_email", False):
            from websauna.system.mail import views
            self.config.scan(views)
            self.config.add_jinja2_search_path('websauna.system.mail:templates', name='.html')

    @event_source
    def configure_templates(self):
        from websauna.system.core import templatecontext  # noQA
        from websauna.system.core.render import get_on_demand_resource_renderer

        # Jinja 2 templates as .html files
        self.config.include('pyramid_jinja2')
        self.config.add_jinja2_renderer('.html')
        self.config.add_jinja2_renderer('.txt')
        self.config.add_jinja2_renderer('.css')
        self.config.add_jinja2_renderer('.xml')

        self.config.include("websauna.system.core.templatecontext")
        self.config.include("websauna.system.core.vars")

        # Add core templates to the search path
        self.config.add_jinja2_search_path('websauna.system.core:templates', name='.html')
        self.config.add_jinja2_search_path('websauna.system.core:templates', name='.txt')
        self.config.add_jinja2_search_path('websauna.system.core:templates', name='.xml')
        self.config.add_jinja2_search_path('websauna.system.core:templates', name='.css')

        # Add the default resource registry for Deform
        self.config.add_request_method(get_on_demand_resource_renderer, 'on_demand_resource_renderer', reify=True)

    @event_source
    def configure_authentication(self):
        """Set up authentication and authorization policies.

        For more information see Pyramid auth documentation.
        """
        from websauna.system.auth.principals import resolve_principals
        from websauna.system.auth.authentication import get_request_user
        from pyramid.authorization import ACLAuthorizationPolicy
        from websauna.system.auth.policy import SessionAuthenticationPolicy

        authn_policy = SessionAuthenticationPolicy(callback=resolve_principals)
        authz_policy = ACLAuthorizationPolicy()
        self.config.set_authentication_policy(authn_policy)
        self.config.set_authorization_policy(authz_policy)

        # We need to carefully be above TM view, but below exc view so that internal server error page doesn't trigger session authentication that accesses the database
        self.config.add_tween("websauna.system.auth.tweens.SessionInvalidationTweenFactory", under="pyramid_tm.tm_tween_factory")

        # Grab incoming auth details changed events
        from websauna.system.auth import subscribers
        self.config.scan(subscribers)

        # Experimental support for transaction aware properties
        try:
            from pyramid_tm.reify import transaction_aware_reify
            self.config.add_request_method(
                callable=transaction_aware_reify(self.config, get_request_user),
                name="user",
                property=True,
                reify=False)
        except ImportError:
            self.config.add_request_method(get_request_user, 'user', reify=True)

    @event_source
    def configure_panels(self):
        self.config.include('pyramid_layout')

    @event_source
    def configure_federated_login(self):
        """Configure federated authentication (OAuth).

        Set up Authomatic login services.

        Read enabled federated authentication methods from the configuration file.
        """

        # TODO: Refactor this to separate functions, not implementation is not very clean

        import authomatic
        from websauna.system.user.interfaces import IAuthomatic, ISocialLoginMapper, IOAuthLoginService
        from websauna.system.user.oauthloginservice import DefaultOAuthLoginService

        settings = self.settings
        secrets = self.secrets

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

        # Pass explicitly a logger so that we can control the log level
        logger = logging.getLogger("authomatic")

        instance = authomatic.Authomatic(config=authomatic_config, secret=authomatic_secret, logger=logger)
        self.config.registry.registerUtility(instance, IAuthomatic)

        self.config.registry.registerAdapter(factory=DefaultOAuthLoginService, required=(IRequest,), provided=IOAuthLoginService)

    @event_source
    def configure_database(self):
        """Configure database.

        * Set up base model

        * Set up mechanism to create database session for requests

        * Set up transaction machinery

        Calls py:func:`websauna.system.model.meta.includeme`.

        """
        from .model.meta import create_transaction_manager_aware_dbsession
        from .model.interfaces import ISQLAlchemySessionFactory

        self.config.include("pyramid_retry")
        self.config.include("pyramid_tm")
        self.config.include(".model.meta")

        self.config.registry.registerAdapter(factory=create_transaction_manager_aware_dbsession, required=(IRequest,), provided=ISQLAlchemySessionFactory)

    @event_source
    def configure_redis(self):
        """Configure Redis connection pool."""
        from websauna.system.core import redis
        self.config.registry.redis = redis.create_redis(self.config.registry)

        # Add logging events
        self.config.scan(redis)

    @event_source
    def configure_instrumented_models(self):
        """Configure models from third party addons and dynamic SQLAlchemy fields which need access to the configuration.

        Third party addons might need references to configurable models which are not available at the import time. One of these models is user - you can supply your own user model. However third party addon models might want to build foreign key relationships to this model. Thus, ``configure_instrumented_models()`` is an initialization step which is called when database setup is half way there and you want to throw in some extra models in.

        This exposes ``Configurator`` to SQLAlchemy through ``websauna.system.model.meta.Base.metadata.pyramid_config`` variable.
        """
        # Expose Pyramid configuration to classes
        from websauna.system.model.meta import Base
        Base.metadata.pyramid_config = self.config

    @event_source
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

        # Internal server error page must be only activated in the production mode, as it clashes with pyramid_debugtoolbar, as both handle uncaught exceptions
        has_debug_toolbar = "pyramid_debugtoolbar" in aslist(settings.get("pyramid.includes", []))
        debug_toolbar_enabled = has_debug_toolbar and asbool(settings.get("debugtoolbar.enabled", True))

        if not debug_toolbar_enabled:
            from websauna.system.core.views import internalservererror
            self.config.scan(internalservererror)

        if settings.get("websauna.error_test_trigger", False):
            from websauna.system.core.views import errortrigger
            self.config.scan(errortrigger)
            self.config.add_route('error_trigger', '/error-trigger')

        from websauna.system.core.views import badcsrftoken
        self.config.scan(badcsrftoken)

    @event_source
    def configure_root(self):
        """Root object defines permissions for route URLs which have not their own traversing context.

        http://pyramid-tutorials.readthedocs.org/en/latest/getting_started/10-security/
        """
        from websauna.system.core.root import Root
        self.config.set_root_factory(Root.root_factory)

    @event_source
    def configure_views(self):
        """Configure views for your application."""

    @event_source
    def configure_sitemap(self):
        """Configure sitemap generation for your site.

        By default this is not configured and nothing is done.
        """

    @event_source
    def configure_static(self):
        """Configure static asset views.

        By default we serve only core Websauna assets. Override this to add more static asset declarations to your app.
        """
        self.static_asset_policy.add_static_view('websauna-static', 'websauna.system:static')

    @event_source
    def configure_sessions(self):
        """Configure session storage."""

        from websauna.system.core.session import set_creation_time_aware_session_factory

        session_secret = self.secrets["session.secret"]

        # TODO: Make more boilerplate here so that we pass secret in more sane way
        self.config.registry.settings["redis.sessions.secret"] = session_secret
        self.config.include("pyramid_redis_sessions")

        # Set a flag to perform Redis session check later and prevent web server start if Redis is down
        self._has_redis_sessions = True

        set_creation_time_aware_session_factory(self.config)

    @event_source
    def configure_admin(self):
        """Configure admin ux.

        Register templates and views for admin interface.
        """
        from websauna.system.admin import subscribers
        from websauna.system.admin import views
        from websauna.system.admin.admin import Admin
        from websauna.system.admin.interfaces import IAdmin
        from websauna.system.admin.modeladmin import configure_model_admin
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

        # Add request.admin variable
        self.config.add_request_method(get_admin, 'admin', reify=True)

    def configure_csrf(self):
        """Configure cross-site request forgery subsystem."""
        self.config.set_default_csrf_options(require_csrf=True)

    @event_source
    def configure_forms(self):
        """Configure subsystems for rendering Deform forms.

        * Deform templates

        * Deform JS and CSS

        * CSRf view mapper
        """
        from websauna.system.form.resources import DefaultFormResources
        from websauna.system.form.interfaces import IFormResources
        from websauna.system.form.deform import configure_zpt_renderer

        # Make Deform widgets aware of our widget template paths
        configure_zpt_renderer(["websauna.system.form:templates/deform"])

        # Include Deform JS and CSS to static serving
        self.static_asset_policy.add_static_view('deform-static', 'deform:static')

        # Overrides for Deform 2 stock JS and CSS
        default_form_resources = DefaultFormResources()
        self.config.registry.registerUtility(default_form_resources, IFormResources)

    @event_source
    def configure_crud(self):
        """CRUD templates and views."""
        # Add our template to search path
        self.config.add_jinja2_search_path('websauna.system.crud:templates', name='.html')
        self.config.add_jinja2_search_path('websauna.system.crud:templates', name='.txt')

        from websauna.system.crud import views
        self.config.scan(views)

    @event_source
    def configure_models(self):
        """Configure all models from your application.

        Import related model modules and scan them.

        Importing anything with :py:class:`websauna.system.model.meta.Base` base class registers this model to an SQLAlchemy model registry for migrations.
        """
        pass

    @event_source
    def configure_user_models(self):
        """Plug in user models.

        This initialization step connects chosen user model to SQLAlchemy model Base. Also set up :py:class:`websauna.system.user.usermixin.SiteCreator` logic - what happens when the first user logs in.
        """
        from websauna.system.model.meta import Base
        from websauna.system.model.utils import attach_model_to_base
        from websauna.system.user import models
        from websauna.system.user.interfaces import IActivationModel
        from websauna.system.user.interfaces import IGroupModel
        from websauna.system.user.interfaces import ISiteCreator
        from websauna.system.user.interfaces import IUserModel
        from websauna.system.user.interfaces import IUserRegistry
        from websauna.system.user.usermixin import SiteCreator
        from websauna.system.user.userregistry import DefaultEmailBasedUserRegistry

        attach_model_to_base(models.User, Base)
        attach_model_to_base(models.Group, Base)
        attach_model_to_base(models.Activation, Base)
        attach_model_to_base(models.UserGroup, Base)

        # Mark active user and group class
        registry = self.config.registry
        registry.registerUtility(models.User, IUserModel)
        registry.registerUtility(models.Group, IGroupModel)
        registry.registerUtility(models.Activation, IActivationModel)

        site_creator = SiteCreator()
        registry.registerUtility(site_creator, ISiteCreator)

        # Which user registry we are using
        registry.registerAdapter(factory=DefaultEmailBasedUserRegistry, required=(IRequest,), provided=IUserRegistry)

    @event_source
    def configure_user(self):
        """Configure user model, sign in and sign up subsystem.

        * User services

        * Sign in and sign up templates and views

        * User events
        """
        from websauna.system.user import subscribers
        from websauna.system.user import views
        from websauna.system.user.credentialactivityservice import DefaultCredentialActivityService
        from websauna.system.user.interfaces import ICredentialActivityService
        from websauna.system.user.interfaces import ILoginService
        from websauna.system.user.interfaces import IRegistrationService
        from websauna.system.user.loginservice import DefaultLoginService
        from websauna.system.user.registrationservice import DefaultRegistrationService

        # Set up login service
        registry = self.config.registry
        registry.registerAdapter(factory=DefaultLoginService, required=(IRequest,), provided=ILoginService)
        registry.registerAdapter(factory=DefaultCredentialActivityService, required=(IRequest,), provided=ICredentialActivityService)
        registry.registerAdapter(factory=DefaultRegistrationService, required=(IRequest,), provided=IRegistrationService)

        self.config.add_jinja2_search_path('websauna.system.user:templates', name='.html')
        self.config.add_jinja2_search_path('websauna.system.user:templates', name='.txt')

        self.config.scan(subscribers)
        self.config.scan(views)
        self.config.add_route('waiting_for_activation', '/waiting-for-activation')
        self.config.add_route('registration_complete', '/registration-complete')
        self.config.add_route('login', '/login')
        self.config.add_route('logout', '/logout')
        self.config.add_route('forgot_password', '/forgot-password')
        self.config.add_route('reset_password', '/reset-password/{code}')
        self.config.add_route('register', '/register')
        self.config.add_route('activate', '/activate/{code}')

    @event_source
    def configure_password(self):
        """Configure system password hashing solution.

        By default use Argon 2

        * https://github.com/hynek/argon2_cffi

        For more information see :py:mod:`websauna.system.user.password`
        """
        from websauna.system.user.password import Argon2Hasher
        from websauna.system.user.interfaces import IPasswordHasher

        hasher = Argon2Hasher()

        registry = self.config.registry
        registry.registerUtility(hasher, IPasswordHasher)

    @event_source
    def configure_model_admins(self):
        import websauna.system.user.admins
        import websauna.system.user.adminviews
        self.config.scan(websauna.system.user.admins)
        self.config.scan(websauna.system.user.adminviews)

    @event_source
    def configure_notebook(self):
        """Setup pyramid_notebook integration."""

        # Check if we have IPython installed
        try:
            pkg_resources.get_distribution('IPython[notebook]')
        except pkg_resources.DistributionNotFound:
            return

        try:
            import websauna.system.notebook.views
            import websauna.system.notebook.adminviews
            import websauna.system.notebook.subscribers
        except ImportError:
            # Have installed IPython[Notebook], but not pyramid_notebook
            return

        self.config.add_route('admin_shell', '/notebook/admin-shell')
        self.config.add_route('shutdown_notebook', '/notebook/shutdown')
        self.config.add_route('notebook_proxy', '/notebook/*remainder')
        self.config.scan(websauna.system.notebook.views)
        self.config.scan(websauna.system.notebook.adminviews)
        self.config.scan(websauna.system.notebook.subscribers)
        self.config.registry.features.add("notebook")

    @event_source
    def configure_tasks(self):
        """Scan all Python modules with asynchoronous and periodic tasks to be imported."""
        try:
            import celery  # noQA
        except ImportError as e:
            # Celery not installed as optional dependency
            return

        # Importing the task is enough to add it to Celerybeat working list
        from websauna.system.devop import tasks  # noQA
        self.config.scan(tasks)

    @event_source
    def configure_tweens(self):
        """Configure tweens."""

    def read_secrets(self) -> dict:
        """Read secrets configuration file.

        Stores API keys, such.
        """
        # Secret configuration diretives
        from websauna.utils.secrets import read_ini_secrets
        from websauna.system.core.interfaces import ISecrets

        settings = self.settings

        secrets_file = settings.get("websauna.secrets_file")
        if not secrets_file:
            return {}

        strict = asbool(settings.get("websauna.secrets_strict", True))

        _secrets = read_ini_secrets(secrets_file, strict=strict)
        self.config.registry.registerUtility(_secrets, ISecrets)
        secret_settings = {k.replace('app:main.', ''): v for k, v in _secrets.items() if k.startswith('app:main.')}
        settings.update(secret_settings)
        self.config.registry.settings.update(secret_settings)
        return _secrets

    def include_addons(self):
        """Override this method to include Websauna addons for your app.

        Websauna addons are created with ``websauna_addon`` scaffold.

        By default do nothing.
        """

    def run(self):
        """Run the initialization and prepare Pyramid subsystems.

        This is the main entry for ramping up a Websauna application.
        We go through various subsystem inits.
        """

        # Avoid running the initializer twice. This might happen e.g. due to a bad testing set up where the initializer creation is not scoped properly. E.g. Jinja template engine will get very confused.
        assert not self._already_run, "Attempted to run initializer twice. Please avoid double initialization as it will lead to problems."

        self.configure_logging()

        # Configure addons before anything else, so we can override bits from addon, like template lookup paths, later easily
        self.include_addons()

        # Serving
        self.configure_templates()
        self.configure_static()

        # Authentication and authorization
        # (Must be before any views are included)
        self.configure_authentication()

        # Forms
        self.configure_csrf()
        self.configure_forms()
        self.configure_crud()

        # Email
        self.configure_mailer()

        # Timed tasks
        self.configure_tasks()

        # Core view and layout related
        self.configure_root()
        self.configure_error_views()
        self.configure_views()
        self.configure_panels()
        self.configure_sitemap()
        self.configure_tweens()

        # Website administration
        self.configure_admin()

        # Addon models
        self.configure_models()

        # Redis (preferably before sessions)
        self.configure_redis()

        # Sessions and users
        self.configure_sessions()
        self.configure_user()
        self.configure_user_forms()
        self.configure_user_models()
        self.configure_password()
        self.configure_federated_login()

        # Configure web shell
        self.configure_notebook()

        # Database and models
        self.configure_instrumented_models()
        self.configure_model_admins()
        self.configure_database()

        # Tests can pass us some extra initialization work on ad hoc
        extra_init = self.global_config.get("extra_init")
        if extra_init:
            resolver = DottedNameResolver()
            extra_init = resolver.resolve(extra_init)
            extra_init(self)

        self._already_run = True

    @event_source
    def sanity_check(self):
        """Perform post-initialization sanity checks.

        This is run on every startup to check that the database table schema matches our model definitions. If there are un-run migrations this will bail out and do not let the problem to escalate later.

        See also: :ref:`websauna.sanity_check`.

        """
        import sqlalchemy.exc
        from websauna.system.model import sanitycheck
        from websauna.system.model.meta import Base
        from websauna.system.model.meta import create_dbsession
        from websauna.system.core import redis

        dbsession = create_dbsession(self.config.registry)

        db_connection_string = self.config.registry.settings.get("sqlalchemy.url")

        try:
            if not sanitycheck.is_sane_database(Base, dbsession):
                raise SanityCheckFailed("The database sanity check failed. Check log for details.")
        except sqlalchemy.exc.OperationalError as e:
            raise SanityCheckFailed("The database {} is not responding.\nMake sure the database is running on your local computer or correctly configured in settings INI file.\nFor more information see https://websauna.org/docs/tutorials/gettingstarted/tutorial_02.html.".format(db_connection_string)) from e

        dbsession.close()

        if self._has_redis_sessions:
            if not redis.is_sane_redis(self.config):
                raise SanityCheckFailed("Could not connect to Redis server.\nWebsauna is configured to use Redis server for session data.\nIt cannot start up without a running Redis server.\nPlease consult your operating system community how to install and start a Redis server.")

    @event_source
    def wrap_wsgi_app(self, app):
        """Perform any necessary WSGI application wrapping.

        Wrap WSGI application to another WSGI application e.g. for the monitoring support. By default support New Relic.
        """

        # TODO: Make this plugin
        # if "NEW_RELIC_CONFIG_FILE" in os.environ:
        # Wrap for New Relic
        # libgcc_s.so.1 must be installed for pthread_cancel to work
        # import newrelic.agent
        # return newrelic.agent.wsgi_application()(app)

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
            sanity_check = asbool(self.global_config["sanity_check"])
        else:
            sanity_check = asbool(self.settings.get("websauna.sanity_check", True))

        if sanity_check:
            self.sanity_check()

        app = self.wrap_wsgi_app(app)

        return app

    @classmethod
    def bootstrap(cls, global_config):
        """Use as WSGI entry point.

        :return:
        """
        init = cls(global_config)
        init.run()
        wsgi_app = init.make_wsgi_app()
        return wsgi_app


def get_init(global_config, settings, init_cls=None) -> Initializer:
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


class DemoInitializer(Initializer):
    """Websauna uses internally to run tests, development server."""

    def configure_views(self):
        # Add home view required to run functional test.
        # This view is never exposed to the applications
        # built upon Websauna.
        super(DemoInitializer, self).configure_views()
        from websauna.system.core.views import home
        self.config.add_route('home', '/')
        self.config.scan(home)


def main(global_config, **settings):
    """Entry point for creating a Pyramid WSGI application."""

    init = DemoInitializer(global_config)
    init.run()
    wsgi_app = init.make_wsgi_app()
    return wsgi_app
