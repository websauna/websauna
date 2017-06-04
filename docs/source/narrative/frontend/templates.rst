.. _templates-narrative:

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

:doc:`Read how views work <views>`.

Template reference
==================

See :doc:`template reference <../../reference/templates>` to get yourself familiar with templates supplied with Websauna.

Jinja primer
============

To learn how :term:`Jinja` template language works read `Jinja Template Designer Documentation <http://jinja.pocoo.org/docs/dev/templates/>`_.

.. _block:

Blocks
======

Base templates consist of blocks which you can fill in.

See :doc:`template reference <../../reference/templates>` for available blocks.

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

URLs
====

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

Variables in URLs
-----------------

Below is an example how to use template variable in :ref:`static_url <filter-static_url>`:

.. code-block:: html+jinja

    {% set img=product_description.images.0 %}
    {% set full_img='trees:static/theme/img/product/' ~ img  %}

    <div id="product-page-header" style="background-image: url({{ full_img|static_url }});">
        <!-- Use product image as the background image for the page -->
    </div>

Images
======

Static images
-------------

The usual process to add an image on your website is

* Include image file in ``static`` folder of your application

* Refer to this image using :ref:`static_url <filter-static_url>` filter in your template.

Example:

.. code-block:: html+jinja

    <img src="{{ 'myapp:static/assets/img/logo-transparent.png'|static_url }}" alt="">

Customizing navigation
======================

Navigation is defined in :ref:`template-site/nav.html`.

Copy ``nav.html`` file to ``yourapp/site`` folder.

Edit the file and add new entries to ``navbar-collapse`` section.

Example:

.. code-block:: html+jinja

    <nav class="navbar navbar-default">
      <div class="container">
        {# Brand and toggle get grouped for better mobile display #}
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#header-navbar-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          {% include "site/logo.html" %}
        </div>

        <div class="collapse navbar-collapse" id="header-navbar-collapse">
          <ul class="nav navbar-nav navbar-left">
            <li class="hidden">
              <a href="#page-top"></a>
            </li>

            <li>
              <a href="{{'invoices'|route_url}}">Bills</a>
            </li>

            <li>
              <a href="#">Top up</a>
            </li>

            <li>
              <a href="#">Send money</a>
            </li>

            <li>
              <a href="#">Withdraw</a>
            </li>
          </ul>

          <ul class="nav navbar-nav navbar-right">
                {# .... #}
          </ul>
        </div>
        {# /.navbar-collapse #}
      </div>
      {# /.container-fluid #}
    </nav>

Formatting decimals
===================

Jinja can use Python string formatting:

.. code-block:: html+jinja

    Price: <strong>${{ '{0:0.2f}'.format(price) }}</strong>

Alternative use :ref:`filter-round` where you can give rounding direction:

.. code-block:: html+jinja

    Price: <strong>${{ price|round(precision=2, method='common') }}</strong>

Advanced
========

Invoking debugger inside templates
----------------------------------

You can start a Python debugger prompt, pdb or any of its flavour, inside a page template. This allows you to inspect the current template rendering context, variables and such.

If you put into the template

.. code-block:: html+jinja

    <h1>Template goes here</h1>

    {{ debug() }}

    <li>
        Item
    </li>

Next time you reload the page the command line debugger will open in your :ref:`ws-pserve` terminal.

Now you can inspect template context.

.. code-block:: pycon

    >>> up
    ... -> return __obj(*args, **kwargs)
    >>> up
    -> <li>
    >>>  context.keys()

    dict_keys(['js_in_head', 'site_email_prefix', 'lipsum', 'render_flash_messages', 'view', 'dict', 'site_tag_line', 'on_demand_resource_renderer', 'joiner', 'site_url', 'panel', 'site_author', 'debug', 'context', 'renderer_info', 'ngettext', 'site_time_zone', 'range', 'request', '_', 'site_name', 'req', 'cycler', 'panels', 'gettext', 'renderer_name'])

    >>> context["request"].admin.get_admin_menu().get_entries()

    ValuesView(OrderedDict([('admin-menu-home', <websauna.system.admin.menu.RouteEntry object at 0x112b74ba8>), ('admin-menu-data', <websauna.system.admin.menu.RouteEntry object at 0x112b74b38>)]))

See :ref:`var-debug` and :ref:`websauna.template_debugger` for more information.

`See more information in template debugging article <https://opensourcehacker.com/2013/05/16/putting-breakpoints-to-html-templates-in-python/>`_.

Accessing Jinja environment
---------------------------

Each template suffix (``.txt``, ``.html``, ``.xml``) has its own Jinja environment.

Example:

.. code-block:: python

    from pyramid_jinja2 import IJinja2Environment

    def find_filters(request):
        env = request.registry.queryUtility(IJinja2Environment, name=".html")
        filters = []
        for name, func in env.filters.items():
            print(name, func)
