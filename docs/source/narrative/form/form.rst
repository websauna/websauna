.. _forms:

============
Deform forms
============

.. contents:: :local:

Introduction
------------

Websauna comes with a form subsystem to easily create and manage various website forms.

In Websauna forming

* Website offers :term:`Deform` form library by default. However you are free to pick your own alternative.

* You can :doc:`automatically generate forms from SQLAlchemy models <./autoform>`

* :doc:`Admin interface does this for your site manager views easily <../crud/admin>`

* :doc:`Widgets can get their CSS and JS included in the page rendering on demand <./resourceregistry>`

* You can also use :doc:`CRUD independently from admin <../crud/crud>`

* Database transactions are tied to successful HTTP request processing, so even if your form processing fails, no partial data is written to the database. This is so called atomic requests behavior.

* :doc:`Cross-site request forgery protection <./csrf>` is mandatory by default as a security feature

* Your forms should implement :doc:`throttling <./throttling>` as a security feature against denial-of-service attacks your application (:term:`DoS`)

* Form subsystem is configured in :py:meth:`websauna.system.Initializer.configure_forms`. If you want to drop in your own forming system override this method.

About Deform
------------

`Deform documentation <http://deform.readthedocs.org/en/latest/>`_ is the best source how to create forms with Deform.

See also `Deform widget samples <http://demo.substanced.net/deformdemo/>`_.

See :py:mod:`websauna.system.user.schemas`, :py:mod:`websauna.system.user.adminviews` and :py:mod:`websauna.system.crud.views` for some more samples.

Basic form life cycle
---------------------

Below is an example how to create and validate one form::

    import colander
    import deform
    from pyramid.httpexceptions import HTTPFound
    from pyramid.httpexceptions import HTTPBadRequest

    from websauna.system.http import Request
    from websauna.system.core import messages
    from websauna.system.form.schema import CSRFSchema
    from websauna.system.form.resourceregistry import ResourceRegistry
    from websauna.system.core.route import simple_route


    class MySchema(CSRFSchema):
        question = colander.Schema(colander.String())


    @simple_route("/form", route_name="my_form", renderer="myapp/my_form.html")
    def my_form(request: Request):

        schema = MySchema().bind(request=request)

        # Create a styled button with some extra Bootstrap 3 CSS classes
        b = deform.Button(name='process', title="Process", css_class="btn-block btn-lg")
        form = deform.Form(schema, buttons=(b, ), resource_registry=ResourceRegistry(request))

        # User submitted this form
        if request.method == "POST":
            if 'process' in request.POST:

                try:
                    appstruct = form.validate(request.POST.items())

                    # TODO: Now you have parsed and validated form data
                    # in appstruct dict.
                    # Do something about it.

                    # Thank user and take him/her to the lading page
                    messages.add(request, kind="info", msg="Thank you for submission")
                    return HTTPFound(request.route_url("home"))

                except deform.ValidationFailure as e:
                    # Render a form version where errors are visible next to the fields,
                    # and the submitted values are posted back
                    rendered_form = e.render()
            else:
                # We don't know which control caused form submission
                return HTTPBadRequest("Unknown form button pressed")
        else:
            # Render a form with initial values
            rendered_form = form.render()

        # This loads widgets specific CSS/JavaScript in HTML code,
        # if form widgets specify any static assets.
        form.resource_registry.pull_in_resources(request, form)

         return locals()


Then the template ``myapp/my_form.html``:

.. code-block:: html+jinja

    {% extends "site/base.html" %}

    {% block content %}
        <h1>Enter some data</h1>

        {{rendered_form|safe}}
    {% endblock content %}

Editable form
-------------

Below is a form example which loads from an existing data source to edit the information there.

``schemas.py``:

.. code-block:: python

    import colander

    from websauna.system.form.schema import CSRFSchema

    class UserProfile(CSRFSchema):

        full_name = colander.SchemaNode(
            colander.String(),
            title="Full name")

        address = colander.SchemaNode(
            colander.String(),
            title="Address",
            default="",
            missing="")

        zipcode = colander.SchemaNode(
            colander.String(),
            title="City",
            default="",
            missing="")

``views.py``:

.. code-block:: python

    def get_user_data(user: User) -> dict:
        """Construct appstruct dict from user."""
        
        # This dict is what form fields will be populated with
        data = {}
        # Get all fields from user data
        data.update(user.user_data)
        # Make sure full_name is empty string and not None
        data["full_name"] = user.full_name or ""
        return data


    def set_user_data(user: User, data: dict):
        """Save data on user object."""
        user.full_name = data.pop("full_name", "")
        # JSONB field "bag of everyhing" and
        # we can directly dump any dictionary of strings there
        user.user_data.update(data)


    @simple_route("/profile", "profile", renderer="views/profile.html", permission="authenticated")
    def profile(request: Request):
        """Allow user to edit his/her profile data."""

        schema = UserProfile().bind(request=request)

        form = deform.Form(schema, buttons=("Save", ))

        # User submitted this form
        if request.method == "POST":
            if 'Save' in request.POST:

                try:
                    appstruct = form.validate(request.POST.items())

                    # Appstruct is nested dictionary struct itself and we can store
                    # it directly on user_data
                    set_user_data(request.user, appstruct)

                    # Thank user and take him/her to the next page
                    messages.add(request, kind="info", msg="User profile updated", msg_id="profile-saved")
                    return HTTPFound(request.route_url("home"))

                except deform.ValidationFailure as e:
                    # Render a form version where errors are visible next to the fields,
                    # and the submitted values are posted back
                    rendered_form = e.render()
            else:
                # We don't know which control caused form submission
                raise HTTPBadRequest("Unknown form button pressed")
        else:
            # Render a form with initial values (empty dictionary by default)
            rendered_form = form.render(get_user_data(request.user))

        return locals()

Creating forms imperatively - data-driven forms
-----------------------------------------------

Colander schemas do not need to be fixed - you can construct them run-time. Here is an example which creates a main form with multiple subforms (rating, feedback text) for each item in the database::

    @simple_route(
        "/review/{delivery_uuid}", 
        route_name="review_public", 
        renderer='views/review.html', 
        append_slash=False)
    def review(request, delivery_uuid):
        """Let user to leave a product for delivery.

        One delivery can contain several product. Each product has Review SQL object instance 
        generated at the time of creation. This form will let review

        """
        delivery_uuid = slug_to_uuid(delivery_uuid)
        delivery = DBSession.query(models.Delivery).filter_by(uuid=delivery_uuid).first()

        # No reason to enter here before the shipment is done
        assert delivery.delivery_status == "delivered"

        # Create form serialized form of all items in this delivery
        reviews = [serialize_review(r) for r in delivery.reviews]
        assert len(reviews) >= 0

        # Dynamically (imperatively) construct a schema where we have N rating subschemas, 
        # for each we leave star rating 1-5 and comment. Each of the items is mapped through UUID.
        rating = colander.Schema(name="single_rating", widget=ReviewFrameWidget())

        # Hidden info we use in the page rendering and mapping POST back to DB items
        rating.add(colander.SchemaNode(
            colander.String(), 
            name="uuid", 
            missing=colander.null, 
            widget=deform.widget.HiddenWidget()))
        rating.add(colander.SchemaNode(
            colander.String(), 
            name="name", 
            missing=colander.null, 
            widget=deform.widget.HiddenWidget()))

        rating.add(colander.SchemaNode(
            colander.Int(), 
            name="rating", 
            missing=colander.null, 
            validator=colander.Range(0, 5), 
            widget=deform.widget.HiddenWidget(css_class="rating")))
        rating.add(colander.SchemaNode(
            colander.String(), 
            name="comment", 
            validator=colander.Length(max=4096), 
            missing="", 
            widget=deform.widget.TextAreaWidget(cols=40, rows=5, template="comment_textarea")))
        ratings = colander.SchemaNode(
            colander.Sequence(), 
            rating, 
            name="ratings", 
            default=reviews, 
            widget=SimpleSequenceWidget())

        schema = CSRFSchema(widget=deform.widget.FormWidget(item_template="item_template_chromeless"))

        # Bind schema to request so CSRF token value is filled for the current session
        schema = schema.bind(request=request)

        schema.add(ratings)

        form = deform.Form(schema, buttons=("submit", "skip"))

.. note::

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

`See Deform documentation <http://docs.pylonsproject.org/projects/deform/en/master/validation.html>`_.

Read only fields
----------------

Below is an example of read-only, populated, fields on a form.

Example:

.. code-block:: python

    """Newsletter admin inteface."""

    import colander
    import deform
    from pyramid.view import view_config
    from pyramid import httpexceptions

    from websauna.system.core import messages
    from websauna.system.core.utils import get_secrets
    from websauna.system.form.schema import CSRFSchema
    from websauna.system.form.resourceregistry import ResourceRegistry
    from websauna.system.http import Request
    from websauna.newsletter.interfaces import INewsletterGenerator


    class NewsletterSend(CSRFSchema):
        """Send a news letter."""

        domain = colander.SchemaNode(
            colander.String(),
            missing=colander.null,
            widget=deform.widget.TextInputWidget(readonly=True),
            title="Mailgun outbound domain",
            description="From secrets.ini",
        )


    @view_config(context=Admin,
        name="newsletter",
        route_name="admin",
        permission="edit",
        renderer="newsletter/admin.html")
    def newsletter(context: Admin, request: Request):
        """Newsletter admin form."""
        schema = NewsletterSend().bind(request=request)

        # Create a styled button with some extra Bootstrap 3 CSS classes
        b = deform.Button(name='process', title="Send", css_class="btn-block btn-lg")
        form = deform.Form(schema, buttons=(b, ), resource_registry=ResourceRegistry(request))

        secrets = get_secrets(request.registry)
        domain = secrets.get("mailgun.domain", "")

        # User submitted this form
        if request.method == "POST":
            # ...
            pass
        else:
            # Default values for read only fields
            rendered_form = form.render({
                "api_key": api_key,
                "domain": domain,
                "mailing_list": mailing_list,
            })

        # This loads widgets specific CSS/JavaScript in HTML code,
        # if form widgets specify any static assets.
        form.resource_registry.pull_in_resources(request, form)

        return locals()

Overriding widget template
--------------------------

This example shows how to override a widget template for any widget. Deform internally uses Chameleon template engine (not :term:`Jinja`)

First register the folder where you have Deform templates in the :py:class:`websauna.system.Initializer` of your app. Example:

.. code-block:: python

        from websauna.system.form.deform import configure_zpt_renderer

        # Register a template path for Deform
        configure_zpt_renderer(["myapp:form/templates/deform"])

Then you can throw in any widget template in that path as .pt file. Example ``textinput_placeholder.py`` that adds support for HTML5 placeholder attribute on ``<input>``. See how we use ``field.widget.placeholder`` attribute to pass data around:

.. code-block:: html

    <!--! This adds placeholder attribute support for TextInput.

        TODO: Drop this template when upstream Deform gains a native support

        http://stackoverflow.com/q/31019326/315168

     -->

    <span tal:define="name name|field.name;
                      css_class css_class|field.widget.css_class;
                      oid oid|field.oid;
                      mask mask|field.widget.mask;
                      mask_placeholder mask_placeholder|field.widget.mask_placeholder;
                      style style|field.widget.style;
                      placeholder field.widget.placeholder|nothing;
                      type field.widget.type|'text';
    "
          tal:omit-tag="">
        <input type="${type}" name="${name}" value="${cstruct}"
               tal:attributes="class string: form-control ${css_class};
                               style style;
                               placeholder placeholder;
                               data-placement python: getattr(field.widget, 'tooltip_placement', None);
                               data-toggle python:'tooltip' if hasattr(field.widget, 'tooltip') else None;
                               title field.widget.tooltip|nothing"
               id="${oid}"/>
        <script tal:condition="mask" type="text/javascript">
          deform.addCallback(
             '${oid}',
             function (oid) {
                $("#" + oid).mask("${mask}",
                     {placeholder:"${mask_placeholder}"});
             });
        </script>
    </span>

Now you can use the template with your :term:`Deform` widget. You can give a template hint to the widget in :term:`Colander` schema:

.. code-block:: python

    class ForgotPasswordSchema(CSRFSchema):
        """Used on forgot password view."""
        email = c.SchemaNode(
            c.Str(),
            title='Email',
            validator=c.All(c.Email(), validate_user_exists_with_email),
            widget=w.TextInputWidget(size=40, maxlength=260, type='email', template="textinput_placeholder", placeholder="youremail@example.com"),
            description="The email address under which you have your account.")


Widget CSS and JavaScript
-------------------------

To plug in CSS or JavaScript code on per widget bases see :ref:`resource registry <resource-registry>`.

Default values
--------------

You can set defaut values by setting ``default`` keyword argument on :py:class:`colander.SchemaNode`.

To have dynamic default arguments you can use :py:func:`colander.deferred`:

.. code-block:: python

    import colander

    from websauna.system.form.schema import CSRFSchema
    from websauna.utils.time import now


    @colander.deferred
    def default_reward_text(node, kw):
        return "Solar reward {}/{}".format(now().year, now().month)


    class MySchema(CSRFSchema):
        label = colander.SchemaNode(colander.String(), default=default_reward_text)

Another example passing `appstruct` to constructed empty form:

.. code-block:: python

    from pyramid.httpexceptions import HTTPFound, HTTPNotFound

    import colander
    import deform

    from websauna.system.form.csrf import CSRFSchema
    from websauna.system.core import messages


    class RenameSchema(CSRFSchema):
        name = colander.SchemaNode(colander.String())
        slug = colander.SchemaNode(colander.String())
        symbol = colander.SchemaNode(colander.String())


    @view_config(context=AssetDescription, route_name="network", name="rename", permission="manage-content", renderer="network/rename.html")
    def rename(asset_desc: AssetDescription, request: Request):
        """Rename asset.

        Allow change it title and symbol, but optionally keep slug intact.
        """

        schema = RenameSchema().bind(request=request)
        asset = asset_desc.asset  # SQLAlchemy instance

        # Create a styled button with some extra Bootstrap 3 CSS classes
        b = deform.Button(name='process', title="Process", css_class="btn-block btn-lg")
        form = deform.Form(schema, buttons=(b,))

        # User submitted this form
        if request.method == "POST":
            if 'process' in request.POST:

                try:
                    appstruct = form.validate(request.POST.items())

                    # Save form data from appstruct
                    asset.name = appstruct["name"]
                    asset.symbol = appstruct["symbol"]
                    asset.other_data["slug"] = appstruct["slug"]

                    # Thank user and take him/her to the next page
                    messages.add(request, kind="info", msg="Renamed to {}".format(asset.name))
                    return HTTPFound(request.resource_url(asset_desc))

                except deform.ValidationFailure as e:
                    # Render a form version where errors are visible next to the fields,
                    # and the submitted values are posted back
                    rendered_form = e.render()
            else:
                # We don't know which control caused form submission
                return HTTPNotFound("Bad POST - no button detected")
        else:

            # Populate default values
            appstruct = {
                "name": asset.name,
                "symbol": asset.symbol,
                "slug": asset.slug,
            }
            # Render a form with initial values
            rendered_form = form.render(appstruct=appstruct)

        return locals()
