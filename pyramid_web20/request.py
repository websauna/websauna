"""Request object augmentation."""

from horus.lib import get_user as _get_user


def get_user(request):
    """Making A “User Object” Available as a Request Attribute.

    http://pyramid-cookbook.readthedocs.org/en/latest/auth/user_object.html
    """
    return get_user(request)

