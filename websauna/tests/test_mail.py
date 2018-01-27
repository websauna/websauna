def test_sample_html_email(web_server, browser):
    """Test that HTML email renderer works."""
    browser.visit(web_server + "/sample-html-email")
    assert browser.is_element_present_by_css("#heading-sample-email")
