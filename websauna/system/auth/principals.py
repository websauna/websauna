"""Resolve principals (groups and pseudo roles) for ACL."""
# Standard Library
import typing as t

# Pyramid
from pyramid.security import Authenticated
from pyramid.settings import asbool
from pyramid.settings import aslist

# Websauna
from websauna.system.http import Request
from websauna.system.user.utils import get_user_registry


def resolve_principals(session_token: str, request: Request) -> t.Optional[t.List[str]]:
    """Get applied groups and other for the user.

    This is a callback for :py:class:`pyramid.authentication.SessionAuthenticationPolicy`.

    * List all groups as ``group:admin`` style strings

    * List super user as ``superuser:superuser`` style string

    :return: None if the user is not logged in, otherwise list of principals assigned to the user site wide.
    """

    user_registry = get_user_registry(request)
    user = user_registry.get_user_by_session_token(session_token)
    if not user:
        return None

    settings = request.registry.settings

    # Read superuser names from the config
    superusers = aslist(settings.get("websauna.superusers"))

    admin_as_superuser = asbool(settings.get("websauna.admin_as_superuser", False))

    if user_registry.can_login(user):

        # Users always get Authenticated special principal
        principals = [Authenticated]

        # All groups for this user
        principals += ['group:{}'.format(g.name) for g in user_registry.get_groups(user)]

        # Give principal for per user permissions
        principals += ['user:{}'.format(user.id)]

        # Allow superuser permission
        if user.username in superusers or user.email in superusers:
            # Superuser explicitly listed in the configuration
            principals.append("superuser:superuser")
        elif admin_as_superuser and ("group:admin" in principals):
            # Automatically promote admins to superusers when doing local development
            principals.append("superuser:superuser")

        return principals

    # User not found, user disabled
    return None
