def test_sample_html_email(web_server, browser):
    """Test that HTML email renderer works."""
    browser.visit(web_server + "/sample-html-email")
    assert browser.status_code == 200