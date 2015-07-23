=====
Forms
=====

Introduction
============

Websauna comes with a form subsystem to easily create and manage various website forms.

* You can automatically generate forms

* Database transactions are tied to successful HTTP request processing, so even if your form processing fails, no partial data is written to the database.

* There exists security tools like cross-site request forgery checking (mandatory) and submission throttling (optional) to protect your site against attacks.

Cross-site request forgery checking
===================================

Cross-site request forgery is a mechanism to prevent malicious sites stealing and manipulating your user data.

Using form classes
------------------

TODO

Checking manually
-----------------

If you are processing HTTP POST submissions without using any framework you can do the following to ensure CSRF protection.

Include ``csrf_token` in `<form>`::

        <form method="POST">
            <input name="csrf_token" type="hidden" value="{{ request.session.get_csrf_token() }}"/>
            <button type="submit" name="confirm">Confirm</button>
        </form>

Check the token in your view handling form submission::

    from pyramid.session import check_csrf_token
    from tomb_routes import simple_route
    from websauna.system.core import messages


    @simple_route("/my-form", route_name="my_form", renderer="my_form.html")
    def my_form(request, delivery_uuid):

        if request.method == "POST":
            if "confirm" in request.POST:
                check_csrf_token(request)

                # ...

                messages.add(request, kind="success", msg="Thank you for submission")
                return HTTPFound(request.route_url("home"))
            else:
                # Should not happen unless malicious
                raise AssertionError("Unknown submit type")

For more information see :py:meth:`websauna.system.form.csrf.check_csrf_token`.


Throttling
==========

Throttling is an activity to limit (anonymous) user actions on the site to a certain rate, so that malicious parties cannot overflow the system (send email invites) or exhibit excessive costs (send SMS).

Throttling submissions in a form
--------------------------------

Preface: You have an action on the site which will send email to an unconfirmed third party. You want to limit the rate of outgoing emails, so that a malicious party cannot use the function to flood third party inboxes.

Example::

    from pyramid.httpexceptions import HTTPTooManyRequests
    from websauna.system.form import rollingwindow

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
                # ... process normally

Throttling form submissions using a Deform validator
----------------------------------------------------

Preface: You have a Deform based form which is open for anonymous submissions. You want to limit the potential problems caused by malicious party by overflooding the form with submissions.

Example::

    import colander as c

    @c.deferred
    def throttle_invites_validator(node, kw):
        """Protect invite functionality from flood attacks."""
        request = kw["request"]

        # Limit to 60 invites / hour
        limit = int(request.registry.settings.get("trees.invite_limit", 60))

        def inner(node, value):
            # Check we don't have many invites going out
            if rollingwindow.check(request.registry, "invite_friends", window=3600, limit=limit):

                # Alert devops through Sentry
                logger.warn("Excessive invite traffic")

                # Tell users slow down
                raise c.Invalid(node, 'Too many outgoing invites at the moment. Please try again later.')

        return inner

Then when you construct the schema instance form form you give validator to it explicitly::

    schema = schemas.InviteFriends(validator=schemas.throttle_invites_validator).bind(request=request, user=request.user)

Testing
=======

See form functional testing in the testing chapter.