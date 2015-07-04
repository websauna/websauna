=====
Forms
=====

Introduction
============

Websauna comes with a form subsystem to easily create and manage various website forms.

* You can automatically generate forms

* Database transactions are tied to successful HTTP request processing, so even if your form processing fails, no partial data is written to the database.

* There exists security tools like cross-site request forgery checking (mandatory) and submission throttling (optional) to protect your site against attacks.

Throttling
==========

TODO

Cross-site request forgery
==========================

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
