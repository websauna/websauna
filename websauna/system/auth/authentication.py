"""The user authentication helper functions."""
from pyramid.settings import aslist
from pyramid.security import unauthenticated_userid
from websauna.system.http import Request
from websauna.system.user.models import User

from websauna.system.user.utils import get_user_registry


def get_user(session_token: str, request: Request) -> User:
    """Extract the logged in user from the request object using Pyramid's authentication framework."""

    # user_id = unauthenticated_userid(request)

    # TODO: Abstract this to its own service like in Warehouse?
    user_registry = get_user_registry(request)

    if session_token is not None:
        user = user_registry.get_user_by_session_token(session_token)

        # Check through conditions why this user would no longer be valid
        if user:
            if not user.can_login():
               # User account disabled while in mid-session
               return None

        return user

    return None


def get_request_user(request: Request) -> User:
    """Reify method for request.user"""
    user_id = request.unauthenticated_userid
    return get_user(user_id, request) if user_id else None


