=====
Forms
=====

Introduction
============

Websauna comes with a form subsystem to easily create and manage various website forms.

In Websauna forming

* Website offers :term:`Deform` form library by default. However you are free to pick your own alternative.

* You can :doc:`automatically generate forms from SQLAlchemy models <./autoform>`

* :doc:`Admin interface does this for your site manager views easily <../modelling/admin>`

* :doc:`Widgets can get their CSS and JS included in the page rendering on demand <./resourceregistry>`

* You can also use :doc:`CRUD independently from admin <../modelling/crud>`

* Database transactions are tied to successful HTTP request processing, so even if your form processing fails, no partial data is written to the database. This is so called atomatic requests behavior.

* :doc:`Cross-site request forgery protection <./csrf>` is mandatory by default as a security feature

* Your forms should implement :doc:`throttling <./throttling>` as a security feature against denial-of-service attacks your application (:term:`DoS`)

* Form subsystem is configured in :py:meth:`websauna.system.Initializer.configure_forms`. If you want to drop in your own forming system override this method.

Deform
======

`Deform documentation <http://deform.readthedocs.org/en/latest/>`_ is the best source how to create forms with Deform.

See also `Deform widget samples <http://demo.substanced.net/deformdemo/>`_.

See :py:mod:`websauna.system.user.schemas`, :py:mod:`websauna.system.user.adminviews` and :py:mod:`websauna.system.crud.views` for some more samples.

Basic form life cycle
---------------------

Below is an example how to create and validate one form::

    from pyramid.httpexceptions import HTTPFound
    import colander
    import deform
    import pyramid_deform

    from websauna.system.core import messages


    class MySchema(pyramid_deform.CSRFSchema):
        question = colander.Schema(colander.String())


    @simple_route("/form", route_name="my_form", renderer="myapp/my_form.html")
    def my_form(request):

        schema = MySchema().bind(request=request)

        # Create a styled button with some extra Bootstrap 3 CSS classes
        b = deform.Button(name='process', title="Process", css_class="btn-block btn-lg")
        form = pyramid_deform.CSRFSchema(schema, buttons=(b, ))

        # User submitted this form
        if request.method == "POST":
            if 'process' in request.POST:

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


Then the template ``myapp/my_form.html``::

.. code-block:: html+jinja

    {% extends "site/base.html" %}

    {% block content %}
        <h1>Enter some data</h1>

        {{rendered_form|safe}}
    {% endblock content %}


Dynamically manipulating widgets
--------------------------------

The widget parameters can be manipulated after constructing the form instance. Example of settings a CSS class::

    def my_view(request):
        # ...
        schema = schemas.DeliveryInformation().bind(request=request)
        form = deform.Form(schema)
        form["additional_driver_information"].widget.css_class = "wide-field"




