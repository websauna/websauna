====================
Outgoing email tests
====================

.. contents:: :local:

Checking if email has been sent by your view
--------------------------------------------

This demostrators how to test if views accessed through Splinter browser have sent email.

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

Check if test code has sent email
---------------------------------

This example shows how to check if test code itself has sent email. In this case, we call email sending event chain directly from unit test, not going through a test web server.

.. code-block:: python

    from sqlalchemy.orm.session import Session
    from pyramid.registry import Registry
    from pyramid_mailer.mailer import DummyMailer


    from websauna.tests.utils import create_user, make_dummy_request, make_routable_request
    from websauna.system.mail.utils import get_mailer


    def test_push_render_email(dbsession: Session, registry, user_id):
        """Create a new activity and generates rendered email notification.."""

        # Create a request with route_url()
        request = make_routable_request(dbsession, registry)

        # Reset test mailer at the beginnign of the test
        mailer = get_mailer(registry)

        # Check we got a right type of mailer for our unit test
        assert isinstance(mailer, DummyMailer)
        assert len(mailer.outbox) == 0

        with transaction.manager:
            u = dbsession.query(User).get(user_id)

            # Create an activity
            a = create_activity(request, "demo_msg", {}, uuid4(), u)

            # Push it through notification channel
            channel = Email(request)
            channel.push_notification(a)

            # DummyMailer updates it outbox immediately, no need to wait transaction.commit
            assert len(mailer.outbox) == 1
