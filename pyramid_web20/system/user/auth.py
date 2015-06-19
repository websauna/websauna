"""The user authentication."""
from pyramid.settings import aslist

from pyramid.security import unauthenticated_userid
from pyramid_web20.system.model import DBSession


def get_user(request):

    from horus.interfaces import IUserClass
    userid = unauthenticated_userid(request)
    user_class = request.registry.queryUtility(IUserClass)

    if userid is not None:
        user = user_class.get_by_id(request, userid)
        if user and not user.can_login():
            # User account disabled while in mid-session
            return None
        return user

    return None


def find_groups(userid, request):
    """Get applied groups and other for the user"""

    from horus.interfaces import IUserClass
    user_class = request.registry.queryUtility(IUserClass)

    # Read superuser names from the config
    superusers = aslist(request.registry.settings.get("pyramid_web20.superusers"))

    user = DBSession.query(user_class).get(userid)
    if user:
        if user.can_login():
            principals = ['group:{}'.format(g.name) for g in user.groups]

        # Allow superuser permission
        if user.username in superusers or user.email in superusers:
            principals.append("superuser:superuser")

        return principals

    # User not found, user disabled
    return None
