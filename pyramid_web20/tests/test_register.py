from pyramid_web20.system.model import DBSession

EMAIL = "example@example.com"
PASSWORD = "ToholamppiMadCowz585"


def get_user():
    from pyramid_web20.system.user.models import User

    return DBSession.query(User).get(1)


def test_register_email(web_server, browser, dbsession):
    """Register on the site and login after activation."""

    # Load user model
    # registry = get_current_registry()
    # User = registry.queryUtility(IUserClass)
    # assert User

    b = browser
    b.visit(web_server)

    b.click_link_by_text("Sign up")

    assert b.is_element_visible_by_css("#sign-up-form")

    b.fill("email", EMAIL)
    b.fill("password", PASSWORD)
    b.fill("password-confirm", PASSWORD)

    b.find_by_name("submit").click()

    assert b.is_element_visible_by_css("#waiting-for-activation")

    # Now peek the Activation link from the database
    user = get_user()
    assert user.activation.code

    activation_link = "{}/activate/{}/{}".format(web_server, user.id, user.activation.code)

    b.visit(activation_link)

    assert b.is_element_visible_by_css("#sign-up-complete")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("Log_in").click()

    # After login we see a profile link to our profile
    assert b.is_element_visible_by_css("#nav-logout")


