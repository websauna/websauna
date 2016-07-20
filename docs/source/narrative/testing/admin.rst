===============
Admin interface
===============

Admin interface integration testing
===================================

Below is example code how to write a integration test against admin interface. The test users various :term:`pytest` fixtures from :py:mod:`websauna.tests.conftest`. We use :py:func:`websauna.tests.utils.create_logged_in_user` to set up a logged in admin browsing session.

.. code-block:: python

    from pyramid.registry import Registry
    from splinter.driver import DriverAPI
    from sqlalchemy.orm import Session

    from websauna.tests.utils import create_logged_in_user


    def test_add_admin_order(dbsession: Session, browser: DriverAPI, web_server: str, registry: Registry):
        """Place order through admin interface."""

        b = browser

        # Create a new admin user and log it into the web site
        create_logged_in_user(dbsession, registry, web_server, browser, admin=True)

        # Go to admin interface
        b.visit("{}/admin/".format(web_server))

        # Click the Add card button on the
        b.find_by_css("#btn-panel-add-order").click()

        # Fill in the add form
        b.fill("name", "Peter Pärker")  # Always test for unicode
        b.fill("email", "no-reply@example.com")
        b.fill("sender_name", "Big Corp Inc.")

        # Submit the form
        b.find_by_css("button[type='submit']").click()

        # Confirm we got "Item added" dialog box at the top of the page
        assert b.is_element_present_by_css("#msg-order-added")


