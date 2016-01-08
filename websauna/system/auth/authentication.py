"""The user authentication helper functions."""
from pyramid.settings import aslist
from pyramid.security import unauthenticated_userid
from websauna.system.http import Request
from websauna.system.user.models import User

from websauna.system.user.utils import get_user_class


def get_user(user_id, request:Request) -> User:
    """Extract the logged in user from the request object using Pyramid's authentication framework."""

    # user_id = unauthenticated_userid(request)

    # TODO: Abstract this to its own service like in Warehouse?
    user_class = get_user_class(request.registry)

    if user_id is not None:
        user = user_class.get_by_id(request, user_id)

        # Check through conditions why this user would no longer be valid
        if user:
            if not user.can_login():
               # User account disabled while in mid-session
               return None

            session_created_at = request.session["created_at"]
            if not user.is_valid_session(session_created_at):
                # Session invalidated because authentication details change
                return None

        return user

    return None


def get_request_user(request:Request) -> User:
    """Reify method for request.user"""

    user_id = unauthenticated_userid(request)
    return get_user(user_id, request) if user_id else None


def find_groups(userid:int, request:Request):
    """Get applied groups and other for the user"""

    dbsession = request.dbsession

    user_class = get_user_class(request.registry)

    # Read superuser names from the config
    superusers = aslist(request.registry.settings.get("websauna.superusers"))

    user = dbsession.query(user_class).get(userid)
    if user:
        if user.can_login():
            principals = ['group:{}'.format(g.name) for g in user.groups]

        # Allow superuser permission
        if user.username in superusers or user.email in superusers:
            principals.append("superuser:superuser")

        return principals

    # User not found, user disabled
    return None
