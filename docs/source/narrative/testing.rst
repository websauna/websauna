=======
Testing
=======

Testing patterns
================

Basic functional testing pattern
--------------------------------

The tests usually follow the following format

* Initialize py.test test with the fixtures needed to run the test: database, web server, browser

* Create data needed to run the test through direct SQLAlchemy model manipulation, including the test user

* Perform the test in the test browser through Splinter interaction

Example test::

    import transaction

    from websauna.system import DBSession
    from websauna.tests.utils import login

    from trees import usermodels


    def test_set_arrival_message(web_server, browser, dbsession, init):
        """Set the Driver arrival message."""

        b = browser

        # Initialize test by creating an user and making him a member of driver group
        with transaction.manager:
            user = create_user()
            g = usermodels.Group(name="driver")
            DBSession.flush()
            g.users.append(user)

        # Login in user we just created
        login(web_server, browser)

        # Go to driver profile
        b.find_by_css("#nav-profile").click()
        b.find_by_css("#nav-profile-driver").click()

        # Update settings
        b.fill("arrival_message", "Driver will be here shortly")
        b.find_by_name("save").click()

        # Check settings were saved successfully
        assert b.is_text_present("Driver settings saved")
        assert b.find_by_name("arrival_message").value == "Driver will be here shortly"



Checking if email has been sent
-------------------------------

Make sure your tests use stdout mailer, as set in your ``test.ini``::

    websauna.mailer = websauna.system.mail.StdoutMailer

Then follow the example to how to detect outgoing mail happening outside the main test thread::

    import transaction

    from websauna.tests.utils import create_user, EMAIL, PASSWORD
    from websauna.system.mail.utils import get_mailer
    from websauna.tests.utils import wait_until


    def test_invite_by_email(web_server, browser, dbsession, init):

        b = browser
        with transaction.manager:
            create_user()

        mailer = get_mailer(init.config.registry)

        # Login
        b.visit(web_server + "/login")
        b.fill("username", EMAIL)
        b.fill("password", PASSWORD)
        b.find_by_name("Log_in").click()

        # We should waiting for the payment m
        b.find_by_css("#nav-invite-friends").click()

        b.fill("email", "example@example.com")
        b.find_by_name("invite").click()

        # Transaction happens in another thread and mailer does do actual sending until the transaction is finished. We need to wait in the test main thread to see this to happen.
        wait_until(callback=lambda: mailer.send_count, expected=1)

