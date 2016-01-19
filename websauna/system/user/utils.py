from authomatic import Authomatic
from pyramid.registry import Registry

from websauna.system.user.interfaces import IGroupModel, IUserModel, IAuthomatic, ISocialLoginMapper, ISiteCreator, ILoginService, IActivationModel, IOAuthLoginService


def get_user_class(registry) -> IUserModel:
    user_class = registry.queryUtility(IUserModel)
    return user_class


def get_group_class(registry) -> IGroupModel:
    group_class = registry.queryUtility(IGroupModel)
    return group_class


def get_activation_model(registry) -> IActivationModel:
    activation_model = registry.queryUtility(IActivationModel)
    return activation_model

def get_site_creator(registry) -> ISiteCreator:
    site_creator = registry.queryUtility(ISiteCreator)
    return site_creator


def get_authomatic(registry) -> Authomatic:
    """Get active Authomatic instance from the registry.

    This is registed in ``Initializer.configure_authomatic()``.
    :param registry:
    :return:
    """
    instance = registry.queryUtility(IAuthomatic)
    return instance


def get_social_login_mapper(registry, provider_id:str) -> ISocialLoginMapper:
    """Get a named social login mapper.

    Example::

        get_social_login_mapper(registry, "facebook")

    """
    return registry.queryUtility(ISocialLoginMapper, name=provider_id)


def get_login_service(registry: Registry) -> ILoginService:
    return registry.queryUtility(ILoginService)


def get_oauth_login_service(registry: Registry) -> IOAuthLoginService:
    return registry.queryUtility(IOAuthLoginService)