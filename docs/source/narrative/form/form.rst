=====
Forms
=====

Introduction
============

Websauna comes with a form subsystem to easily create and manage various website forms.

* You can automatically generate forms

* Database transactions are tied to successful HTTP request processing, so even if your form processing fails, no partial data is written to the database.

* There exists security tools like cross-site request forgery checking (mandatory) and submission throttling (optional) to protect your site against attacks.

Basic form life cycle (Deform)
==============================

Below is an example how to create and validate one form::

    from pyramid.httpexceptions import HTTPFound
    import deform

    from websauna.system.core import messages

    # XXX: Add @view_config() here
    def my_view(request):

        schema = MySchema().bind(request=request)

        # Create a styled button with some extra Bootstrap 3 CSS classes
        b = deform.Button(name='start_order', title="Begin", css_class="btn-block btn-lg")
        form = deform.Form(schema, buttons=(b, ))

        # User submitted this form
        if request.method == "POST":
            if 'start_order' in request.POST:

                try:
                    appstruct = form.validate(request.POST.items())

                    # Save form data from appstruct

                    # Thank user and take him/her to the next page
                    messages.add(request, kind="info", message="Thank you for submission")
                    return HTTPFound(request.route_url("another_page_displayed_after_succesful_submission"))

                except deform.ValidationFailure as e:
                    # Render a form version where errors are visible next to the fields,
                    # and the submitted values are posted back
                    rendered_form = e.render()
            else:
                # We don't know which control caused form submission
                raise AssertionError("Unknown form button pressed")
        else:
            # Render a form with initial values
            rendered_form = form.render()

         return locals()


Then the template ``sample_form.html``::

.. code-block:: html

    {% extends "site/base.html" %}

    {% block content %}
        <div class="row">
            <div class="col-md-12">

                <h1>Enter some data</h1>

                {{rendered_form|safe}}

            </div>
        </div>
    {% endblock content %}


Cross-site request forgery checking
===================================

Cross-site request forgery (:term:`CSRF`)  is a mechanism to prevent malicious sites stealing and manipulating your user data.

Websauna enables CSRF protection to all views by default. This is done by :py:meth:`websauna.system.Initializer.configure_forms` which enables :py:class:`websauna.system.core.tweens.EnforcedCSRFCheck` tween.

Deform forms
------------

Always subclass your form schema from :py:class:`pyramid_deform.CSRFSchema`.

Example::

    pass

Hand-written forms
------------------

Include ``csrf_token` in `<form>`::

    <form method="POST">
        <input name="csrf_token" type="hidden" value="{{ request.session.get_csrf_token() }}">
        <button type="submit" name="confirm">Confirm</button>
    </form>


Checking manually
-----------------

If you want to process HTTP POST submissions without the automatic check you can check it manually.

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

Resource registry and widget JS and CSS
=======================================

Deform supports resource registry (:py:class:`websauna.system.form.resourceregistry.ResourceRegistry`) which widgets can use to signal they want a particular CSS and JS file to be present in the page rendering

* Form is constructed with ``resource_registry`` argument

* When the form is finalized, before the page rendering starts call :py:meth:`websauna.system.form.resourceregistry.ResourceRegistry.pull_resources`

* This will go through the form widget stack and extract CSS and JS files from widgets. The required files are passed to :py:class:`websauna.system.core.render.OnDemandResourceRenderer`

* JS is included in ``site/javascript.html`` template and CSS is included in site ``site/css.html` template

* By default ``<script>`` tags comes before closing of ``</body>``. If any Deform widgets require JS all ``<script>`` goes to ``<head>``. This is due to current Deform template limitations.

Deform comes with some default Bootstrap-compatible JS and CSS files, see :py:attr:`deform.widget.default_resources`. Resource registry can also manage bundling of the resources, so that instead of pulling the actual JS file it pulls a bundle where this JS file is present.

Formatting
==========

Dynamically manipulating widgets
--------------------------------

The widget parameters can be manipulated after constructing the form instance. Example of settings a CSS class::

    def my_view(request):
        # ...
        schema = schemas.DeliveryInformation().bind(request=request)
        form = deform.Form(schema)
        form["additional_driver_information"].widget.css_class = "wide-field"



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