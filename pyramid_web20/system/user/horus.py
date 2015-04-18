from horus.resources import UserFactory
from horus.schemas import LoginSchema
from horus.schemas import RegisterSchema
from horus.schemas import ForgotPasswordSchema
from horus.schemas import ResetPasswordSchema
from horus.schemas import ProfileSchema
from horus.forms import SubmitForm
from horus.resources import RootFactory
from horus.interfaces import IUIStrings
from horus.interfaces import IUserClass
from horus.interfaces import IActivationClass
from horus.interfaces import ILoginForm
from horus.interfaces import ILoginSchema
from horus.interfaces import IRegisterForm
from horus.interfaces import IRegisterSchema
from horus.interfaces import IForgotPasswordForm
from horus.interfaces import IForgotPasswordSchema
from horus.interfaces import IResetPasswordForm
from horus.interfaces import IResetPasswordSchema
from horus.interfaces import IProfileForm
from horus.interfaces import IProfileSchema
from horus.lib import get_user
from horus.lib import render_flash_messages_from_queues
from horus import models
from horus.strings import UIStringsBase
from pyramid.events import BeforeRender
from pyramid.path import DottedNameResolver

from hem.config import get_class_from_config

import inspect



def include_routes(config):
    """Add routes to the config."""
    # config.add_route('login', '/login')
    # config.add_route('logout', '/logout')
    # config.add_route('register', '/register')
    # config.add_route('activate', '/activate/{user_id}/{code}',
    #                 factory=UserFactory)
    config.add_route('forgot_password', '/forgot_password')
    config.add_route('reset_password', '/reset_password/{code}')

    config.add_route('profile', '/profile/{user_id}',
                     factory=UserFactory,
                     traverse="/{user_id}")
    config.add_route('edit_profile', '/profile/{user_id}/edit',
                     factory=UserFactory,
                     traverse="/{user_id}")

    # config.add_route('admin', '/admin')
    # config.add_route('admin_users_index', '/admin/users')
    # config.add_route('admin_users_create', '/admin/users/new')
    # config.add_route('admin_users_edit',
    #                  '/admin/users/{user_id}/edit',
    #                  factory=UserFactory,
    #                  traverse="/{user_id}")
    #
    # config.add_static_view(name='horus-static', path='horus:static',
    #                        cache_max_age=3600)



def scan(config, module):
    r = DottedNameResolver()
    module = r.maybe_resolve(module)
    module = inspect.getmodule(module)

    model_mappings = {
        models.UserMixin: IUserClass,
        models.ActivationMixin: IActivationClass,
    }

    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            # don't register the horus mixins
            if obj.__module__ == 'horus.models':
                continue

            for mixin, interface in model_mappings.items():
                if isinstance(obj, type) and issubclass(obj, mixin):
                    config.registry.registerUtility(obj, interface)


def includeme(config):
    settings = config.registry.settings
    # str('user') returns a bytestring under Python 2 and a
    # unicode string under Python 3, which is what we need:
    # config.add_request_method(get_user, str('user'), reify=True)
    config.set_root_factory(RootFactory)

    config.add_directive('scan_horus', scan)

    if not config.registry.queryUtility(IUserClass):
        try:
            user_class = get_class_from_config(settings, 'horus.user_class')
            config.registry.registerUtility(user_class, IUserClass)
        except:
            # maybe they are using scan?
            pass

    if not config.registry.queryUtility(IActivationClass):
        try:
            activation_class = get_class_from_config(settings,
                                                     'horus.activation_class')
            config.registry.registerUtility(activation_class,
                                            IActivationClass)
        except:
            # maybe they are using scan?
            pass

    defaults = [
        (IUIStrings, UIStringsBase),
        (ILoginSchema, LoginSchema),
        (IRegisterSchema, RegisterSchema),
        (IForgotPasswordSchema, ForgotPasswordSchema),
        (IResetPasswordSchema, ResetPasswordSchema),
        (IProfileSchema, ProfileSchema)
    ]

    forms = [
        ILoginForm, IRegisterForm, IForgotPasswordForm,
        IResetPasswordForm, IProfileForm
    ]

    for iface, default in defaults:
        if not config.registry.queryUtility(iface):
            config.registry.registerUtility(default, iface)

    for form in forms:
        if not config.registry.queryUtility(form):
            config.registry.registerUtility(SubmitForm, form)

    def on_before_render(event):
        fn = render_flash_messages_from_queues
        event['render_flash_messages'] = lambda: fn(event['request'])

    config.add_subscriber(on_before_render, BeforeRender)

    include_routes(config)
    # import horus
    # config.scan(package=horus, ignore=str('horus.tests'))
