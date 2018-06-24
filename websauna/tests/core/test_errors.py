import requests


SPOOF_CSRF_JS = """
(function() {
console.log('Preparing CSRF spoofing');
$("input[name='csrf_token']").val("xxx");
console.log("Finished geospoofing");
})();
"""


def test_internal_server_error(customized_web_server, browser):
    """When things go KABOOM show a friendly error page."""

    web_server = customized_web_server({"websauna.log_internal_server_error": False})

    b = browser
    b.visit("{}/error-trigger".format(web_server))

    # After login we see a profile link to our profile
    assert b.is_element_visible_by_css("#it-is-broken")


def test_not_found(web_server, browser):
    """Show not found page on unknown URL."""

    b = browser
    missing_url = "{}/foobar".format(web_server)
    b.visit(missing_url)

    assert b.is_element_visible_by_css("#not-found")

    # Splinter b.status_code is not reliable
    resp = requests.get(missing_url)
    assert resp.status_code == 404


def test_forbidden(web_server, browser):
    """Access controlled page should not be available."""

    b = browser
    b.visit("{}/admin/".format(web_server))

    assert b.is_element_visible_by_css("#forbidden")


def test_csrf_fail(web_server, browser):
    """Bad CSRF token shoud give us an error page."""

    b = browser
    b.visit(web_server + "/login")
    b.fill("username", "x")
    b.fill("password", "y")

    b.evaluate_script(SPOOF_CSRF_JS.replace("\n", " "))

    b.find_by_name("login_email").click()

    # Only present on our custom page
    assert b.is_element_present_by_css("#heading-bad-csrf-token")
