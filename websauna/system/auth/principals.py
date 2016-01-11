"""Resolve principals (groups and pseudo roles) for ACL."""
from pyramid.settings import asbool
from pyramid.settings import aslist

from websauna.system.http import Request
from websauna.compat.typing import List
from websauna.compat.typing import Optional
from websauna.system.user.utils import get_user_class


def resolve_principals(userid:int, request:Request) -> Optional[List[str]]:
    """Get applied groups and other for the user.

    This is a callback for :py:class:`pyramid.authentication.SessionAuthenticationPolicy`.

    * List all groups as ``group:admin`` style strings

    * List super user as ``superuser:superuser`` style string
    """

    dbsession = request.dbsession

    user_class = get_user_class(request.registry)
    settings = request.registry.settings

    # Read superuser names from the config
    superusers = aslist(settings.get("websauna.superusers"))

    admin_as_superuser = asbool(settings.get("websauna.admin_as_superuser", False))

    user = dbsession.query(user_class).get(userid)
    if user and user.can_login():

        principals = ['group:{}'.format(g.name) for g in user.groups]

        # Allow superuser permission
        if user.username in superusers or user.email in superusers or (admin_as_superuser and "group:admin" in principals):
            principals.append("superuser:superuser")

        return principals

    # User not found, user disabled
    return None