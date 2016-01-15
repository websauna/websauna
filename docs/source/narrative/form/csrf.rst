=====================================
Cross-site request forgery protection
=====================================

.. contents:: :local:

Cross-site request forgery (:term:`CSRF`)  is a mechanism to prevent malicious sites stealing and manipulating your user data.

Websauna enables CSRF protection to all views by default. This is done by :py:meth:`websauna.system.Initializer.configure_forms` which enables :py:class:`websauna.system.core.tweens.EnforcedCSRFCheck` tween.

Deform forms
------------

Always subclass your form schema from :py:class:`pyramid_deform.CSRFSchema`.

Example::

    import colander
    import deform
    import pyramid_deform

    class MySchema(pyramid_deform.CSRFSchema):

        question = colander.Schema(colander.String())

Then later you can use it as::

    form = Form(MySchema)

Hand-written forms
------------------

Include ``csrf_token`` in ``<form>``::

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

Disabling CSRF check
--------------------

For individual views you can use :py:func:`websauna.system.core.csrf.csrf_exempt` decorator.

If your site needs more comprehensive whitelisting strategy you can implement your own :py:func:`websauna.system.core.csrf._check_csrf`. This is configured in :py:meth:`websauna.system.Initializer.configure_forms`.