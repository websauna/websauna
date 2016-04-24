from authomatic import Authomatic
from pyramid.interfaces import IRequest
from pyramid.registry import Registry

from websauna.system.http import Request
from websauna.system.user.interfaces import IGroupModel, IUserModel, IAuthomatic, ISocialLoginMapper, ISiteCreator, ILoginService, IActivationModel, IOAuthLoginService, IUserRegistry, ICredentialActivityService, IRegistrationService


def get_user_class(registry: Registry) -> IUserModel:
    user_class = registry.queryUtility(IUserModel)
    return user_class


def get_group_class(registry: Registry) -> IGroupModel:
    group_class = registry.queryUtility(IGroupModel)
    return group_class


def get_activation_model(registry: Registry) -> IActivationModel:
    activation_model = registry.queryUtility(IActivationModel)
    return activation_model


def get_site_creator(registry: Registry) -> ISiteCreator:
    site_creator = registry.queryUtility(ISiteCreator)
    return site_creator


def get_authomatic(registry: Registry) -> Authomatic:
    """Get active Authomatic instance from the registry.

    This is registed in ``Initializer.configure_authomatic()``.
    :param registry:
    :return:
    """
    instance = registry.queryUtility(IAuthomatic)
    return instance


def get_social_login_mapper(registry: Registry, provider_id:str) -> ISocialLoginMapper:
    """Get a named social login mapper.

    Example::

        get_social_login_mapper(registry, "facebook")

    """
    return registry.queryUtility(ISocialLoginMapper, name=provider_id)


def get_login_service(request: Request) -> ILoginService:
    assert IRequest.providedBy(request)
    return request.registry.queryAdapter(request, ILoginService)


def get_oauth_login_service(request: Request) -> IOAuthLoginService:
    assert IRequest.providedBy(request)
    return request.registry.queryAdapter(request, IOAuthLoginService)


def get_user_registry(request: Request) -> IUserRegistry:
    return request.registry.queryAdapter(request, IUserRegistry)


def get_credential_activity_service(request: Request) -> ICredentialActivityService:
    assert IRequest.providedBy(request)
    return request.registry.queryAdapter(request, ICredentialActivityService)


def get_registration_service(request: Request) -> IRegistrationService:
    assert IRequest.providedBy(request)
    return request.registry.queryAdapter(request, IRegistrationService)
