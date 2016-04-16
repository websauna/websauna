"""TODO: This is a hacked in Horus support that will be removed in the future versions."""

from horus.resources import UserFactory
from horus.schemas import LoginSchema
from horus.schemas import RegisterSchema
from horus.schemas import ForgotPasswordSchema
from horus.schemas import ResetPasswordSchema
from horus.schemas import ProfileSchema
from horus.forms import SubmitForm
from horus.resources import RootFactory
from websauna.system.user.interfaces import IUIStrings
from websauna.system.user.interfaces import IUserClass
from websauna.system.user.interfaces import IActivationClass
from websauna.system.user.interfaces import ILoginForm
from websauna.system.user.interfaces import ILoginSchema
from websauna.system.user.interfaces import IRegisterForm
from websauna.system.user.interfaces import IRegisterSchema
from websauna.system.user.interfaces import IForgotPasswordForm
from websauna.system.user.interfaces import IForgotPasswordSchema
from websauna.system.user.interfaces import IResetPasswordForm
from websauna.system.user.interfaces import IResetPasswordSchema
from websauna.system.user.interfaces import IProfileForm
from websauna.system.user.interfaces import IProfileSchema
from horus.lib import get_user
from horus.lib import render_flash_messages_from_queues
from horus import models
from horus.strings import UIStringsBase
from pyramid.events import BeforeRender
from pyramid.path import DottedNameResolver

from hem.config import get_class_from_config

import inspect



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
