=========
Templates
=========

.. contents:: :local:

Introduction
============

Websauna uses :term:`Jinja` template language as its default template engine for rendering HTML. You are free to choose any other template engine for your templates. See :term:`Pyramid` support for `different template engines <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/templates.html#available-add-on-template-system-bindings>`_.

How templating works
====================

URLs are never directly connected to template files. Instead, URLs point to views. Views prepare the data as input for the page template. This usually includes doing database look ups and processing form posts. A view returns a dictionary which contains items which can be later substituted in template using ``{{ variable }}`` syntax.

:doc:`Read how views work <./views>`.

Template reference
==================

See :doc:`template reference <../../reference/templates>` to get yourself familiar with templates supplied with Websauna.

Jinja primer
============

To learn how :term:`Jinja` template language works read `Jinja Template Designer Documentation <http://jinja.pocoo.org/docs/dev/templates/>`_.

Filters and context variables
=============================

See :doc:`template content variable and filter reference <../../reference/templatecontext>` to get yourself familiar with Jinja variables and filters supplied with Websauna.

Template loading order
======================

Template loader in set up in such a way that it tries to

* Load the first matching template relative to the ``templates`` folder

* Load template from your Websauna ``myapp/templates`` folder

* Load from any Websauna addon

* Load from Websauna core package

For example it would first try ``myapp/templates/site/logo.html`` and then ``websauna/system/core/templates/site/logo.html``.

All ``templates`` folder are connected to the :term:`Jinja` template loader in :py:class:`websauna.system.Initializer`. See

* :py:meth:`websauna.system.Initializer.configure_templates`.

* :py:meth:`websauna.system.Initializer.configure_admin`.

* :py:meth:`websauna.system.Initializer.configure_crud`.

Rendering a template
====================

Rendering for a view
--------------------

The template is usually rendered by returning a template context dictionary from a view function. The template context dictionary is passed to a template defined by ``renderer`` parameter in the view config. ``renderer`` must be a path to a file defined in one of the template paths.

Example::

    from websauna.system.http import Request
    from websauna.system.core.route import simple_route

    @simple_route("/", route_name="home", renderer='myapp/home.html')
    def home(request: Request):
        """Render site homepage."""
        project_name = "Mikko's awesome cow hiphop music videos"
        return locals()

Then you can have a template:

.. code-block:: html+jinja

    {% extends "site/base.html" %}

    {% block content %}
        Welcome to {{ project_name }}
    {% endblock %}

Manual rendering
----------------

You can manually render a template by calling ``pyramid.renderers.render``. Example::

    from pyramid.renderers import render

    def my_utility_function(request, first_name, last_name):
        output = render("hello_world.txt", dict(first_name=first_name, last_name=last_name), request=request)

Alternatively if you know the output will be a HTTP response you can use ``pyramid.renderers.render_to_response``::

    from pyramid.renderers import render_to_response

    def my_view(request):
        return render_to_response("hello_world.html", dict(first_name="Mikko", last_name="Ohtamaa"), request=request)

Permission checks
=================

Use :py:meth:`pyramid.request.Request.has_permission` to check if the user has the named permission in the current context.

Example: checking if a user has a permission on certain resources inside admin:

.. code-block:: html+jinja

    {% block panel_buttons %}

        {% if request.has_permission('view', context) %}
            <a id="btn-panel-list-{{ model_admin.id }}" class="btn btn-default btn-admin-list" href="{{ model_admin|model_url('listing') }}">
                List
            </a>
        {% endif %}


        {% if request.has_permission('add', context) %}
            <a id="btn-panel-add-{{ model_admin.id }}" class="btn btn-default btn-admin-list" href="{{ model_admin|model_url('add') }}">
                Add
            </a>
        {% endif %}
    {% endblock %}

Example: check if a user has permission to view :term:`admin`:

.. code-block: html+jinja

  {% if request.admin %}
     {% if request.has_permission('view', context=request.admin) %}
        <li>
          <a href="{{'admin_home'|route_url}}">
             Admin
          </a>
        </li>
    {% endif %}
  {% endif %}

Linking
=======

Traversing links
----------------

If you have a traversable object and want to build a link for it

* First get a handle of corresponding traversing Resource object

* Then call ``request.resource_url()`` or use template ``model_url`` filter to build a link

* Admin object has a helper function ``get_admin_resource()`` to get a ``Resource`` of any SQLAlchemy instance managed in the model admin

Example how to build a link to the ``customer`` user instance in a ``delivery`` template context variable. The view name is ``sms-user``:

.. code-block:: html

    <a href="{{ admin.get_admin_resource(delivery.customer)|model_url('sms-user') }}" id="btn-sms-user" class="btn btn-default">
        Send SMS to customer
    </a>

The actual view definition looks like:

.. code-block:: python

    @view_config(context=admin.UserAdmin.Resource, name="sms-user", route_name="admin", permission='edit', renderer="admin/sms_user.html")
    def sms_user(context, request):
        user = context.get_object()
        # ...

Images
======

Static images
-------------

The usual process to add an image on your website is

* Include image file in ``static`` folder of your application

* Refer to this image using :ref:`static_url` filter in your template.

Example:

.. code-block:: html+jinja

    <img src="{{ 'myapp:static/assets/img/logo-transparent.png'|static_url }}" alt="">

Advanced
========

Accessing Jinja environment
---------------------------

Each template suffix (``.txt``, ``.html``, ``.xml``) has its own Jinja environment.

Example::

    from pyramid_jinja2 import IJinja2Environment

    def find_filters(request):
        env = request.registry.queryUtility(IJinja2Environment, name=".html")
        filters = []
        for name, func in env.filters.items():
            print(name, func)
