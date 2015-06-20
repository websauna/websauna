import os
from decimal import Decimal
from websauna.system.model import now
from websauna.system.model import DBSession

from websauna.system.user.usermixin import check_empty_site_init

#: The default test login name
import transaction

EMAIL = "example@example.com"

#: The default test password
PASSWORD = "ToholamppiMadCowz585"


def create_user(email=EMAIL, password=PASSWORD, admin=False):
    from websauna.system.user.models import User
    from websauna.system.user.models import Group
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


def get_user(email=EMAIL):
    from websauna.system.user.models import User
    return DBSession.query(User).filter_by(email=EMAIL).first()




def create_logged_in_user(web_server, browser, admin=False):
    """For a web browser test session, creates a new user and logs it in."""

    with transaction.manager:
        create_user(admin=admin)

    b = browser
    b.visit("{}/{}".format(web_server, "login"))

    assert b.is_element_visible_by_css("#login-form")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("Log_in").click()

    # After login we log out link to confirm login has succeeded
    assert b.is_element_visible_by_css("#nav-logout")
