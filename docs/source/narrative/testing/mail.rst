==================
Checking for email
==================

Checking if email has been sent
-------------------------------

Make sure your tests use stdout mailer, as set in your ``test.ini``:

.. code-block:: ini

    websauna.mailer = websauna.system.mail.StdoutMailer

Then follow the example to how to detect outgoing mail happening outside the main test thread:

.. code-block:: python

    import transaction

    from websauna.tests.utils import create_user, EMAIL, PASSWORD
    from websauna.system.mail.utils import get_mailer
    from websauna.tests.utils import wait_until


    def test_invite_by_email(web_server, browser, dbsession, init):

        b = browser
        with transaction.manager:
            create_user()

        # Reset test mailer at the beginnign of the test
        mailer = get_mailer(init.config.registry)
        mailer.send_count = 0

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

