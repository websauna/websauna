======================
User sessions in tests
======================

.. contents:: :local:

Accesing session cookie with Splinter
=====================================

Below is an example how you can export a session cookie from :term:`Splinter` browser and then use this with :py:mod:`requests`. This is especially useful for checking non-HTML responses that :term:`Selenium` is not able to cope with.

.. code-block:: python

    def test_csv_export_users(dbsession, registry, browser, web_server):
        """Test CSV export functionality."""

        b = browser

        create_logged_in_user(dbsession, registry, web_server, browser, admin=True)

        unicode_bomb = "toholammin kevätkylvöt"

        with transaction.manager:
            u = dbsession.query(User).first()
            u.username = unicode_bomb

        b.find_by_css("#nav-admin").click()
        b.find_by_css("#btn-panel-list-user").click()
        assert b.is_element_present_by_css("#btn-crud-csv-export")  # This button would trigger the download of CSV that we normally cannot test with Selenium

        # Copy session cookie over to request, so we can do an authenticated user request using requests lib
        cookies = b.driver.get_cookies()

        # Convert to plain dict
        cookies = {c["name"]: c["value"] for c in cookies}
        resp = requests.get("{}/admin/models/user/csv-export".format(web_server), cookies=cookies)

        assert resp.status_code == 200
        assert resp.headers["Content-Type"] == "text/csv; charset=utf-8"
        assert unicode_bomb in resp.text
