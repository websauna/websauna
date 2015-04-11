def test_frontpage(web_server, session_browser, ini_settings):

    b = session_browser
    b.visit(web_server)

    site_name = ini_settings["pyramid_web20.site_name"]
    element = b.find_by_css("h1#front-page-title")

    assert len(element) == 1
    assert element.text == site_name
