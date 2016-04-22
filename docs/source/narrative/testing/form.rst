================
Form submissions
================

Testing form submissions
------------------------

Preface: You want to test your form submission works in success and error situations.

Example form handler view:

.. code-block:: python

    """Subscribe to newsletter."""
    import logging

    import deform
    import deform.widget
    import colander as c

    from pyramid.httpexceptions import HTTPTooManyRequests
    from websauna.system.form.schema import CSRFSchema
    from websauna.system.core.route import simple_route

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
                       messages.add(request, kind="success", msg_id="msg-thank-ou", msg="Thank you! Check your inbox {} for information and coupon code.".format(email))
                    else:
                        messages.add(request, kind="error", msg="Email address {} is already subscribed.".format(email), msg_id="#msg-already-subscribed")

                except deform.ValidationFailure as e:
                    rendered_form = e.render()

        return locals()

Then you can bang it with the following functional test case:

.. code-block:: python

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
        assert b.is_element_present_by_css("#msg-thank-you")

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
        assert b.is_element_present_by_css("#msg-already-subscribed")

        # Check we don't get double entry
        with transaction.manager:
            assert DBSession.query(NewsletterSubscriber).count() == 1

