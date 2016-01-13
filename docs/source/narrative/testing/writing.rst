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


Testing form submissions
------------------------

Preface: You want to test your form submission works in success and error situations.

Example form handler view::

    """Subscribe to newsletter."""
    import logging

    import deform
    import deform.widget
    import colander as c

    from pyramid.httpexceptions import HTTPTooManyRequests
    from pyramid_deform import CSRFSchema
    from tomb_routes import simple_route

    from websauna.system.core import messages
    from websauna.system.mail import send_templated_mail
    from websauna.system.model import now
    from websauna.system.form import rollingwindow

    from trees.models import NewsletterSubscriber

    #: Which session flag tells that the visitor already went through newsletter dialog
    SESSION_SUBSCRIBE_KEY = "subscribed_newsletter"


    logger = logging.getLogger(__name__)


    class SubscribeNewsLetter(CSRFSchema):

        email = c.SchemaNode(
            c.String(),
            validator=c.Email(),
            widget=deform.widget.TextInputWidget(template="textinput_placeholder", type="email",  placeholder="Type in your email here"),
        )


    def get_newsletter_form(request):
        schema = SubscribeNewsLetter().bind(request=request)
        form = deform.Form(schema, buttons=("subscribe", ))
        return form


    @simple_route("/newsletter", route_name="newsletter", renderer='views/newsletter.html', append_slash=False)
    def newsletter(request):
        """Subscribe to news letter from handling."""

        form = get_newsletter_form(request)
        rendered_form = form.render()

        if request.method == "POST":

            # Limit to 60 subscriptions / hour
            limit = int(request.registry.settings.get("trees.newsletter_subscription_limit", 60))

            if rollingwindow.check(request.registry, "invite_friends", window=3600, limit=limit):
                # Alert devops through Sentry
                logger.warn("Newsletter subscription overflow")
                return HTTPTooManyRequests("Too many subscriptions to the newsletter. Please wait 10 minutes and try again.")

            if "subscribe" in request.POST:
                controls = request.POST.items()
                try:
                    appstruct = form.validate(controls)

                    email = appstruct["email"]
                    referrer = request.referrer
                    ip = request.client_addr

                    subscription, created = NewsletterSubscriber.get_or_create_subscriber(email, referrer, ip)

                    # Send email on subsequent submissions as there might have been failed email delivery
                    send_templated_mail(request, [email], "views/email/welcome", locals())

                    if created:
                       messages.add(request, kind="success", msg="Thank you! Check your inbox {} for information and coupon code.".format(email))
                    else:
                        messages.add(request, kind="error", msg="Email address {} is already subscribed.".format(email))

                except deform.ValidationFailure as e:
                    rendered_form = e.render()

        return locals()

Then you can bang it with the following functional test case::

    import transaction

    from trees.models import NewsletterSubscriber
    from websauna.system.model import DBSession



    def test_subscribe_newsletter(dbsession, web_server, browser):
        """Visitor can subscribe to a newsletter."""

        b = browser
        b.visit(web_server + "/newsletter")

        b.fill("email", "foobar@example.com")
        b.find_by_name("subscribe").click()

        # Displayed as a message after succesful form subscription
        assert b.is_text_present("Thank you!")

        # Check we get an entry
        with transaction.manager:
            assert DBSession.query(NewsletterSubscriber).count() == 1
            subscription = DBSession.query(NewsletterSubscriber).first()
            assert subscription.email == "foobar@example.com"
            assert subscription.ip == "127.0.0.1"



    def test_subscribe_newsletter_twice(dbsession, web_server, browser):
        """The second newsletter subscription attempt gives error message."""

        b = browser
        b.visit(web_server + "/newsletter")
        b.fill("email", "foobar@example.com")
        b.find_by_name("subscribe").click()

        # And again
        b.visit(web_server + "/newsletter")
        b.fill("email", "foobar@example.com")
        b.find_by_name("subscribe").click()

        # Error message displayed if the user tries to subscribe twice
        assert b.is_text_present("already subscribed")

        # Check we don't get double entry
        with transaction.manager:
            assert DBSession.query(NewsletterSubscriber).count() == 1

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

