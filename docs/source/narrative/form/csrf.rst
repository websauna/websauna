=====================================
Cross-site request forgery protection
=====================================

.. contents:: :local:

Introduction
------------

Cross-site request forgery (:term:`CSRF`)  is a mechanism to prevent malicious sites stealing and manipulating your user data.

Websauna enables CSRF protection to all views by default `using Pyramid's CSRF mechanism <http://docs.pylonsproject.org/projects/pyramid/en/master/narr/sessions.html#preventing-cross-site-request-forgery-attacks>`_.

Deform forms
------------

This explains how to include a hidden CSRF input field on your :term:`Deform` based forms.

Always subclass your form schema from :py:class:`websauna.system.form.schema.CSRFSchema`.

Example::

    import colander
    import deform
    from websauna.system.form.schema import CSRFSchema

    class MySchema(CSRFSchema):

        question = colander.Schema(colander.String())

Then later you can use it as::

    form = Form(MySchema)


Alternatively you can retrofit ``csrf_token`` to an existing schema using :py:func:`websauna.system.form.schema.add_csrf`.

Hand-written forms
------------------

Include ``csrf_token`` in ``<form>``:

.. code-block:: html+jinja

    <form method="POST">
        <input name="csrf_token" type="hidden" value="{{ request.session.get_csrf_token() }}">
        <button type="submit" name="confirm">Confirm</button>
    </form>


Checking CSRF manually
----------------------

If you want to process HTTP POST submissions without the automatic check you can check it manually.

Check the token in your view handling form submission::

    from pyramid.session import check_csrf_token
    from websauna.system.core.route import simple_route
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

You can disable the CSRF check for individual views by setting ``require_csrf=False`` in view config.

Example:

.. code-block:: python

    # Allows POST with csrf_token field
    @view_config(route_name="csrf_exempt_sample", require_csrf=False)
    def csrf_exempt_sample(request):
        return Response("OK")

