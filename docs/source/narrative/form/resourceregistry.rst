.. _resource-registry:

============================================
Resource registry, widget CSS and JavaScript
============================================

.. contents:: :local:

Introduction
============

:term:`Deform` supports a resource registry allowing widgets to signal they want particular :term:`CSS` and :term:`JavaScript` files to be present in page rendering. E.g. a date picker widget tells it needs date picking JavaScript and CSS files to be present in rendered :term:`HTML`. Then these static assets will be placed in the `<head>` section of HTML.

.. note::

    Most widgets work without additional JS or CSS files. Only complex widgets need additional asset support. For more information see :py:attr:`deform.widget.default_resources`.


You can include JS and CSS from a Deform form using :py:meth:`websauna.system.form.resourceregistry.ResourceRegistry.pull_resources`. This will walk through all form widgets and include widget specific assets in a rendering loop.

Example usage:

.. code-block:: python

    import colander
    import deform
    from deform import Form

    from websauna.system.form.schema import CSRFSchema
    from websauna.system.form.resourceregistry import ResourceRegistry


    class MySchema(CSRFSchema):
        """Ask for email."""

        email = colander.SchemaNode(
            colander.Str(),
            title='Email',
            widget=deform.widget.TextInputWidget(size=40, maxlength=260))



    @simple_route("/form", route_name="my_form", renderer="myapp/my_form.html")
    def my_form(request):

        schema = MySchema().bind(request=request)

        form = Form(schema, resource_registry=ResourceRegistry(request))

        # User submitted this form
        if request.method == "POST":
            # ...
            pass

         # This will populate self.request.on_demand_resource_renderer
         # with JS and CSS static assets from widgets
         form.resource_registry.pull_in_resources(request, form)

         return locals()


Details
=======

* Websauna's resource registry is :py:class:`websauna.system.form.resourceregistry.ResourceRegistry`

* Form is constructed with ``resource_registry`` argument

* When the form is finalized, before the page rendering starts call :py:meth:`websauna.system.form.resourceregistry.ResourceRegistry.pull_resources`

* This will go through the form widget stack and extract CSS and JS files from widgets. The required files are passed to :py:class:`websauna.system.core.render.OnDemandResourceRenderer`

* JS is included in ``site/javascript.html`` template and CSS is included in site ``site/css.html`` template.

* By default ``<script>`` tags comes before closing of ``</body>``. If any Deform widgets require JS all ``<script>`` goes to ``<head>``. This is due to current Deform template limitations.

Deform comes with some default Bootstrap-compatible JS and CSS files, see :py:attr:`deform.widget.default_resources`. Resource registry can also manage bundling of the resources, so that instead of pulling the actual JS file it pulls a bundle where this JS file is present.

See also

* :ref:`css.html template <template-site/css.html>`

* :ref:`javascript.html template <template-site/javascript.html>`

* :py:meth:`websauna.system.form.resourceregistry.ResourceRegistry.pull_resources`

* :py:class:`websauna.system.form.resourceregistry.ResourceRegistry`

* :py:class:`websauna.system.core.render.OnDemandResourceRenderer`