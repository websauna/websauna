from authomatic import Authomatic

from websauna.system.user.interfaces import IGroupClass, IUserClass, IAuthomatic


def get_user_class(registry) -> IUserClass:
    user_class = registry.queryUtility(IUserClass)
    return user_class


def get_group_class(registry) -> IGroupClass:
    group_class = registry.queryUtility(IGroupClass)
    return group_class


def get_authomatic(registry) -> Authomatic:
    """Get active Authomatic instance from the registry.

    This is registed in ``Initializer.configure_authomatic()``.
    :param registry:
    :return:
    """
    instance = registry.queryUtility(IAuthomatic)
    return instance


class ISocialLogin(object):
    pass


def get_social_login_mapper(registry, provider_id:str) -> ISocialLogin:
    return registry.queryUtility(ISocialLogin, name=provider_id)