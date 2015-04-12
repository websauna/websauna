"""The user authentication."""

from . import models

from pyramid.security import unauthenticated_userid
from horus.interfaces import IUserClass


def get_user(request):

    userid = unauthenticated_userid(request)
    user_class = request.registry.queryUtility(IUserClass)

    if userid is not None:
        user = user_class.get_by_id(request, userid)
        if not user.can_login():
            # User account disabled while in mid-session
            return None
        return user

    return None


def find_groups(userid, request):
    """TODO: Not yet there.

    This function is called when you do ``authenticated_userid(request)`` but currently not used.
    """

    user = models.DBSession.query(models.User).get(userid)
    if user:
        if user.can_login():
            return []

    # User not found, user disabled
    return None
