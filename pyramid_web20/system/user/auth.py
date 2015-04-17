"""The user authentication."""

from pyramid_web20 import models

from pyramid.security import unauthenticated_userid


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
    """TODO: Not yet there.

    This function is called when you do ``authenticated_userid(request)`` but currently not used.
    """

    from horus.interfaces import IUserClass
    user_class = request.registry.queryUtility(IUserClass)

    user = models.DBSession.query(user_class).get(userid)
    if user:
        if user.can_login():
            return ['group:{}'.format(g.name) for g in user.groups]

    # User not found, user disabled
    return None
