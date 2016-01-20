"""Resolve principals (groups and pseudo roles) for ACL."""
from pyramid.settings import asbool
from pyramid.settings import aslist

from websauna.system.http import Request
from websauna.compat.typing import List
from websauna.compat.typing import Optional
from websauna.system.user.utils import get_user_registry


def resolve_principals(session_token:str, request:Request) -> Optional[List[str]]:
    """Get applied groups and other for the user.

    This is a callback for :py:class:`pyramid.authentication.SessionAuthenticationPolicy`.

    * List all groups as ``group:admin`` style strings

    * List super user as ``superuser:superuser`` style string
    """

    # TODO: Abstract this to its own service like in Warehouse?
    user_registry = get_user_registry(request)
    user = user_registry.get_user_by_session_token(session_token)
    if not user:
        return None

    settings = request.registry.settings

    # Read superuser names from the config
    superusers = aslist(settings.get("websauna.superusers"))

    admin_as_superuser = asbool(settings.get("websauna.admin_as_superuser", False))

    if user_registry.can_login(user):

        principals = ['group:{}'.format(g.name) for g in user_registry.get_groups(user)]

        # Allow superuser permission
        if user.username in superusers or user.email in superusers or (admin_as_superuser and "group:admin" in principals):
            principals.append("superuser:superuser")

        return principals

    # User not found, user disabled
    return None