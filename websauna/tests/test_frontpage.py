def test_frontpage(web_server, browser, ini_settings):
    """Open the front page as anonymous user."""
    b = browser
    b.visit(web_server)

    site_name = ini_settings["websauna.site_name"]
    element = b.find_by_css("h1#front-page-title")

    assert len(element) == 1
    assert element.text == site_name
