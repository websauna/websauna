"""The user authentication."""
from pyramid.settings import aslist

from pyramid.security import unauthenticated_userid
from websauna.system.user.utils import get_user_class


def get_user(request):

    user_id = unauthenticated_userid(request)
    user_class = get_user_class(request.registry)

    if user_id is not None:
        user = user_class.get_by_id(request, user_id)
        if user and not user.can_login():
            # User account disabled while in mid-session
            return None
        return user

    return None


def find_groups(userid, request):
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
