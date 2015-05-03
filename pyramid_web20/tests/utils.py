import os
from decimal import Decimal
from pyramid_web20.models import now
from pyramid_web20.models import DBSession

from pyramid_web20.system.user.usermixin import check_empty_site_init

#: The default test login name
EMAIL = "example@example.com"

#: The default test password
PASSWORD = "ToholamppiMadCowz585"


def create_user(email=EMAIL, password=PASSWORD, admin=False):
    from pyramid_web20.system.user.models import User
    from pyramid_web20.system.user.models import Group
    user = User(email=email, password=password)
    user.user_registration_source = User.USER_MEDIA_DUMMY
    DBSession.add(user)
    DBSession.flush()
    user.username = user.generate_username()

    assert user.can_login()

    # First user, make it admin
    if admin:
        check_empty_site_init(user)
        admin_grp = DBSession.query(Group).first()
        assert admin_grp
        user.groups.append(admin_grp)
        assert user.is_admin()

    return user


