"""User utilities."""
# Standard Library
import typing as t

# Pyramid
from pyramid.interfaces import IRequest
from pyramid.registry import Registry

from authomatic import Authomatic

# Websauna
from websauna.system.http import Request
from websauna.system.user.interfaces import IActivationModel
from websauna.system.user.interfaces import IAuthomatic
from websauna.system.user.interfaces import ICredentialActivityService
from websauna.system.user.interfaces import IGroupModel
from websauna.system.user.interfaces import ILoginService
from websauna.system.user.interfaces import IOAuthLoginService
from websauna.system.user.interfaces import IRegistrationService
from websauna.system.user.interfaces import ISiteCreator
from websauna.system.user.interfaces import ISocialLoginMapper
from websauna.system.user.interfaces import IUserModel
from websauna.system.user.interfaces import IUserRegistry


def get_user_class(registry: Registry) -> t.Type[IUserModel]:
    """Get the class implementing IUserModel.

    :param registry: Pyramid registry.
    :return: Class implementing IUserModel.
    """
    user_class = registry.queryUtility(IUserModel)
    return user_class


def get_group_class(registry: Registry) -> t.Type[IGroupModel]:
    """Get the class implementing IGroupModel.

    :param registry: Pyramid registry.
    :return: Class implementing IGroupModel.
    """
    group_class = registry.queryUtility(IGroupModel)
    return group_class


def get_activation_model(registry: Registry) -> t.Type[IActivationModel]:
    """Get the class implementing IActivationModel.

    :param registry: Pyramid registry.
    :return: Class implementing IActivationModel.
    """
    activation_model = registry.queryUtility(IActivationModel)
    return activation_model


def get_site_creator(registry: Registry) -> ISiteCreator:
    """Get the class implementing ISiteCreator.

    :param registry: Pyramid registry.
    :return: Class implementing ISiteCreator.
    """
    site_creator = registry.queryUtility(ISiteCreator)
    return site_creator


def get_authomatic(registry: Registry) -> Authomatic:
    """Get active Authomatic instance from the registry.

    This is registered in ``Initializer.configure_authomatic()``.
    :param registry: Pyramid registry.
    :return: Instance of Authomatic.
    """
    instance = registry.queryUtility(IAuthomatic)
    return instance


def get_social_login_mapper(registry: Registry, provider_id: str) -> ISocialLoginMapper:
    """Get a named social login mapper.

    Example::

        get_social_login_mapper(registry, "facebook")

    :param registry: Pyramid registry.
    :param provider_id: Provider id of a social login mapper.
    :return: Implementation of ISocialLoginMapper.
    """
    return registry.queryUtility(ISocialLoginMapper, name=provider_id)


def get_login_service(request: Request) -> ILoginService:
    """Get the login service.

    :param request: Pyramid request.
    :return: Implementation of ILoginService.
    """
    assert IRequest.providedBy(request)
    return request.registry.queryAdapter(request, ILoginService)


def get_oauth_login_service(request: Request) -> IOAuthLoginService:
    """Get the oauth login service.

    :param request: Pyramid request.
    :return: Implementation of IOAuthLoginService.
    """
    assert IRequest.providedBy(request)
    return request.registry.queryAdapter(request, IOAuthLoginService)


def get_user_registry(request: Request) -> IUserRegistry:
    """Get the user registry..

    :param request: Pyramid request.
    :return: Implementation of IUserRegistry.
    """
    return request.registry.queryAdapter(request, IUserRegistry)


def get_credential_activity_service(request: Request) -> ICredentialActivityService:
    """Get the credential activity service.

    :param request: Pyramid request.
    :return: Implementation of ICredentialActivityService.
    """
    assert IRequest.providedBy(request)
    return request.registry.queryAdapter(request, ICredentialActivityService)


def get_registration_service(request: Request) -> IRegistrationService:
    """Get the registration service.

    :param request: Pyramid request.
    :return: Implementation of IRegistrationService.
    """
    assert IRequest.providedBy(request)
    return request.registry.queryAdapter(request, IRegistrationService)
