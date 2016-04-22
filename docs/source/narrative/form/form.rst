============
Forms basics
============

.. contents:: :local:

Introduction
============

Websauna comes with a form subsystem to easily create and manage various website forms.

In Websauna forming

* Website offers :term:`Deform` form library by default. However you are free to pick your own alternative.

* You can :doc:`automatically generate forms from SQLAlchemy models <./autoform>`

* :doc:`Admin interface does this for your site manager views easily <../crud/admin>`

* :doc:`Widgets can get their CSS and JS included in the page rendering on demand <./resourceregistry>`

* You can also use :doc:`CRUD independently from admin <../crud/crud>`

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

    from websauna.system.core import messages
    from websauna.system.form.schema import CSRFSchema


    class MySchema(CSRFSchema):
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


Then the template ``myapp/my_form.html``:

.. code-block:: html+jinja

    {% extends "site/base.html" %}

    {% block content %}
        <h1>Enter some data</h1>

        {{rendered_form|safe}}
    {% endblock content %}


Creating forms imperatively - data-driven forms
-----------------------------------------------

Colander schemas do not need to be fixed - you can construct them run-time. Here is an example which creates a main form with multiple subforms (rating, feedback text) for each item in the database::

    @simple_route("/review/{delivery_uuid}", route_name="review_public", renderer='views/review.html', append_slash=False)
    def review(request, delivery_uuid):
        """Let user to leave a product for delivery.

        One delivery can contain several product. Each product has Review SQL object instance generated at the time of creation. This form will let review

        """
        delivery_uuid = slug_to_uuid(delivery_uuid)
        delivery = DBSession.query(models.Delivery).filter_by(uuid=delivery_uuid).first()

        # No reason to enter here before the shipment is done
        assert delivery.delivery_status == "delivered"

        # Create form serialized form of all items in this delivery
        reviews = [serialize_review(r) for r in delivery.reviews]
        assert len(reviews) >= 0

        # Dynamically (imperatively) construct a schema where we have N rating subschemas, for each we leave star rating 1-5 and comment. Each of the items is mapped through UUID.
        rating = colander.Schema(name="single_rating", widget=ReviewFrameWidget())

        # Hidden info we use in the page rendering and mapping POST back to DB items
        rating.add(colander.SchemaNode(colander.String(), name="uuid", missing=colander.null, widget=deform.widget.HiddenWidget()))
        rating.add(colander.SchemaNode(colander.String(), name="name", missing=colander.null, widget=deform.widget.HiddenWidget()))

        rating.add(colander.SchemaNode(colander.Int(), name="rating", missing=colander.null, validator=colander.Range(0, 5), widget=deform.widget.HiddenWidget(css_class="rating")))
        rating.add(colander.SchemaNode(colander.String(), name="comment", validator=colander.Length(max=4096), missing="", widget=deform.widget.TextAreaWidget(cols=40, rows=5, template="comment_textarea")))
        ratings = colander.SchemaNode(colander.Sequence(), rating, name="ratings", default=reviews, widget=SimpleSequenceWidget())

        schema = CSRFSchema(widget=deform.widget.FormWidget(item_template="item_template_chromeless"))

        # Bind schema to request so CSRF token value is filled for the current session
        schema = schema.bind(request=request)

        schema.add(ratings)

        form = deform.Form(schema, buttons=("submit", "skip"))

.. note ::

    TODO: Parts of the example are old - for example there is no longer global DBSession.

Dynamically manipulating widgets
--------------------------------

The widget parameters can be manipulated after constructing the form instance. Example of settings a CSS class::

    def my_view(request):
        # ...
        schema = schemas.DeliveryInformation().bind(request=request)
        form = deform.Form(schema)
        form["additional_driver_information"].widget.css_class = "wide-field"


Validation
----------

Here is an example data-driven validator::

    import colander
    from websauna.system.form.schema import CSRFSchema


    def validate_unique_user_email(node, value, **kwargs):
    """Make sure we cannot enter the same username twice."""

        request = node.bindings["request"]
        dbsession = request.dbsession
        User = get_user_class(request.registry)
        if dbsession.query(User).filter_by(email=value).first():
            raise colander.Invalid(node, "Email address already taken")


    class MySchema(CSRFSchema):
        email = colander.SchemaNode(colander.String(), validator=validate_unique_user_email)

Widget CSS and JavaScript
-------------------------

See :ref:`resource registry <resource-registry>`.
